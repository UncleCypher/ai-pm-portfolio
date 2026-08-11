from mova_support.application import DiagnosisService
from mova_support.domain import (
    DeviceIdentity,
    DiagnosisOutcome,
    DiagnosisRequest,
    UnderstandingResult,
)
from mova_support.nlu import UnderstandingProvider


def make_request(message: str, locale: str = "zh-CN") -> DiagnosisRequest:
    return DiagnosisRequest(
        message=message,
        locale=locale,
        country="CN" if locale == "zh-CN" else "US",
        device=DeviceIdentity(model="P50 Ultra", firmware_version="1.0.0"),
    )


def test_returns_ranked_hypotheses_and_next_step() -> None:
    response = DiagnosisService().diagnose(make_request("机器回不了基站，也充不进去电"))

    assert response.outcome == DiagnosisOutcome.SELF_SERVICE
    assert response.symptoms[0].code == "cannot_dock"
    assert response.hypotheses[0].cause_code == "dock_path_blocked"
    assert response.next_step is not None
    assert response.citations


def test_unknown_problem_asks_for_more_evidence() -> None:
    response = DiagnosisService().diagnose(make_request("机器感觉不太对"))

    assert response.outcome == DiagnosisOutcome.NEED_MORE_EVIDENCE
    assert response.hypotheses == []
    assert "错误码" not in response.reply
    assert len(response.suggested_replies) >= 4


def test_unknown_dock_problem_gets_contextual_question() -> None:
    response = DiagnosisService().diagnose(make_request("基站最近不太正常"))

    assert response.outcome == DiagnosisOutcome.NEED_MORE_EVIDENCE
    assert response.clarifying_question == "基站具体出现了哪种现象？"
    assert any("集尘" in reply for reply in response.suggested_replies)


def test_general_language_becomes_specific_diagnosis() -> None:
    response = DiagnosisService().diagnose(make_request("最近没以前好用了，清理后地上的灰还是很多"))

    assert response.outcome == DiagnosisOutcome.SELF_SERVICE
    assert response.symptoms[0].code == "weak_cleaning"
    assert response.next_step is not None
    assert response.next_step.step_id == "inspect_air_path"


class WrongLanguageProvider(UnderstandingProvider):
    def understand(self, message: str, locale: str, model: str) -> UnderstandingResult:
        return UnderstandingResult(
            language="en",
            intent="device_fault",
            sentiment="neutral",
            symptom_codes=["navigation_or_map"],
            normalized_problem="导航异常",
            confidence=0.9,
            source="llm",
        )


class UnknownIssueProvider(UnderstandingProvider):
    def understand(self, message: str, locale: str, model: str) -> UnderstandingResult:
        return UnderstandingResult(
            language="zh",
            intent="device_fault",
            sentiment="neutral",
            symptom_codes=[],
            normalized_problem="机器外壳出现不明形变",
            out_of_taxonomy=True,
            proposed_symptom_label="外壳异常形变",
            confidence=0.88,
            source="llm",
        )


class MustNotRunProvider(UnderstandingProvider):
    def understand(self, message: str, locale: str, model: str) -> UnderstandingResult:
        raise AssertionError("critical reports must not be sent to the model")


def test_requested_locale_overrides_model_detected_language() -> None:
    response = DiagnosisService(understanding=WrongLanguageProvider()).diagnose(
        make_request("机器乱跑")
    )

    assert response.language == "zh"
    assert response.next_step is not None
    assert "请" in response.next_step.instruction
    assert response.reply.startswith("我已识别设备为")


def test_high_confidence_unknown_issue_is_preserved_and_escalated() -> None:
    response = DiagnosisService(understanding=UnknownIssueProvider()).diagnose(
        make_request("机器外壳鼓起来了，但不是电池的位置")
    )

    assert response.outcome == DiagnosisOutcome.HUMAN_REVIEW
    assert response.human_ticket_id is not None
    assert response.hypotheses == []
    assert "不会强行" in response.reply


def test_critical_problem_creates_human_ticket() -> None:
    response = DiagnosisService(understanding=MustNotRunProvider()).diagnose(
        make_request("电池膨胀，而且有烧焦味")
    )

    assert response.outcome == DiagnosisOutcome.HUMAN_REVIEW
    assert response.human_ticket_id is not None
    assert response.next_step is None
