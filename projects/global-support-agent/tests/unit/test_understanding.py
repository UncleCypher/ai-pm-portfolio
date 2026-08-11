import httpx
import pytest

from mova_support.domain import UnderstandingResult
from mova_support.nlu import (
    HeuristicUnderstandingProvider,
    OpenAICompatibleConfig,
    OpenAICompatibleUnderstandingProvider,
    ResilientUnderstandingProvider,
    UnderstandingProvider,
)


def test_general_language_maps_to_specific_cleaning_problem() -> None:
    result = HeuristicUnderstandingProvider().understand(
        "最近感觉没以前好用了，地上的灰总是还在",
        "zh-CN",
        "P50 Ultra",
    )

    assert result.symptom_codes[0] == "weak_cleaning"
    assert result.confidence > 0.5


def test_general_navigation_language_is_normalized() -> None:
    result = HeuristicUnderstandingProvider().understand(
        "它现在像无头苍蝇一样到处乱转，有的地方就是不去",
        "zh-CN",
        "P50 Ultra",
    )

    assert result.symptom_codes[0] == "navigation_or_map"


class FailingProvider(UnderstandingProvider):
    def understand(self, message: str, locale: str, model: str) -> UnderstandingResult:
        raise httpx.TimeoutException("model timeout")


def test_model_failure_falls_back_to_local_understanding() -> None:
    provider = ResilientUnderstandingProvider(primary=FailingProvider())

    result = provider.understand("垃圾还在机器里，基站没吸走", "zh-CN", "P50 Ultra")

    assert result.source == "heuristic"
    assert result.symptom_codes[0] == "auto_empty"


class MockModelResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"language":"zh","intent":"device_fault",'
                            '"sentiment":"neutral","symptom_codes":'
                            '["navigation_or_map","invented_code"],'
                            '"normalized_problem":"导航路径异常",'
                            '"missing_information":[],"confidence":0.91}'
                        )
                    }
                }
            ]
        }


def test_model_interface_accepts_structured_output_and_filters_unknown_codes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args: object, **kwargs: object) -> MockModelResponse:
        return MockModelResponse()

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenAICompatibleUnderstandingProvider(
        OpenAICompatibleConfig(
            base_url="https://model.example/v1",
            api_key="test-key",
            model="test-model",
        )
    )

    result = provider.understand("机器走路很奇怪", "zh-CN", "P50 Ultra")

    assert result.source == "llm"
    assert result.symptom_codes == ["navigation_or_map"]
    assert result.normalized_problem == "导航路径异常"
