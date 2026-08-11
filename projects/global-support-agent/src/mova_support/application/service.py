from uuid import uuid4

from mova_support.diagnostics import evaluate_safety, find_knowledge, symptoms_from_codes
from mova_support.domain import DiagnosisOutcome, DiagnosisRequest, DiagnosisResponse
from mova_support.nlu import (
    HeuristicUnderstandingProvider,
    ResilientUnderstandingProvider,
    UnderstandingProvider,
)
from mova_support.tools import FakeSupportTools


class DiagnosisService:
    def __init__(
        self,
        tools: FakeSupportTools | None = None,
        understanding: UnderstandingProvider | None = None,
    ) -> None:
        self._tools = tools or FakeSupportTools()
        self._understanding = understanding or ResilientUnderstandingProvider(primary=None)

    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResponse:
        session_id = request.session_id or uuid4()
        safety = evaluate_safety(request.message, request.locale)
        # Critical reports must not be sent to a remote model. Safety routing is
        # rule-owned and can complete with the deterministic local normalizer.
        understanding = (
            HeuristicUnderstandingProvider().understand(
                request.message,
                request.locale,
                request.device.model,
            )
            if safety.requires_human
            else self._understanding.understand(
                request.message,
                request.locale,
                request.device.model,
            )
        )
        # The user-selected locale is authoritative. Model-detected language is
        # diagnostic metadata only and must never switch the response language.
        language = "zh" if request.locale.lower().startswith("zh") else "en"

        if safety.requires_human:
            ticket_id = self._tools.create_human_ticket(
                session_id=session_id,
                model=request.device.model,
                reason=",".join(safety.matched_rules),
            )
            return DiagnosisResponse(
                session_id=session_id,
                language=language,
                intent="safety_incident",
                sentiment=understanding.sentiment,
                normalized_problem=understanding.normalized_problem,
                understanding_source=understanding.source,
                understanding_confidence=understanding.confidence,
                symptoms=[],
                safety=safety,
                hypotheses=[],
                outcome=DiagnosisOutcome.HUMAN_REVIEW,
                reply=safety.user_message or self._human_review_message(language),
                human_ticket_id=ticket_id,
            )

        symptoms = symptoms_from_codes(understanding.symptom_codes, request.message)
        matched = find_knowledge(symptoms)
        if not matched:
            if (
                understanding.source == "llm"
                and understanding.out_of_taxonomy
                and understanding.confidence >= 0.65
            ):
                ticket_id = self._tools.create_human_ticket(
                    session_id=session_id,
                    model=request.device.model,
                    reason="unclassified:"
                    + (understanding.proposed_symptom_label or understanding.normalized_problem),
                )
                reply = (
                    "这个现象暂不在标准故障库中，我不会强行给出不可靠的判断。"
                    "已保留问题描述并转交人工专员进一步确认。"
                    if language == "zh"
                    else (
                        "This symptom is not yet covered by the standard fault catalog. "
                        "I will not force an unreliable diagnosis; the description has "
                        "been preserved for specialist review."
                    )
                )
                return DiagnosisResponse(
                    session_id=session_id,
                    language=language,
                    intent=understanding.intent,
                    sentiment=understanding.sentiment,
                    normalized_problem=understanding.normalized_problem,
                    understanding_source=understanding.source,
                    understanding_confidence=understanding.confidence,
                    symptoms=[],
                    safety=safety,
                    hypotheses=[],
                    outcome=DiagnosisOutcome.HUMAN_REVIEW,
                    reply=reply,
                    human_ticket_id=ticket_id,
                )
            question, suggestions = self._build_clarification(request.message, language)
            return DiagnosisResponse(
                session_id=session_id,
                language=language,
                intent=understanding.intent,
                sentiment=understanding.sentiment,
                normalized_problem=understanding.normalized_problem,
                understanding_source=understanding.source,
                understanding_confidence=understanding.confidence,
                symptoms=[],
                safety=safety,
                hypotheses=[],
                outcome=DiagnosisOutcome.NEED_MORE_EVIDENCE,
                reply=question,
                clarifying_question=question,
                suggested_replies=suggestions,
            )

        primary = matched[0]
        next_step = primary.next_step_zh if language == "zh" else primary.next_step_en
        return DiagnosisResponse(
            session_id=session_id,
            language=language,
            intent=understanding.intent,
            sentiment=understanding.sentiment,
            normalized_problem=understanding.normalized_problem,
            understanding_source=understanding.source,
            understanding_confidence=understanding.confidence,
            symptoms=symptoms,
            safety=safety,
            hypotheses=list(primary.hypotheses),
            next_step=next_step,
            outcome=DiagnosisOutcome.SELF_SERVICE,
            reply=self._step_message(language, request.device.model, next_step.instruction),
            citations=[primary.source],
        )

    @staticmethod
    def _build_clarification(message: str, language: str) -> tuple[str, list[str]]:
        normalized = message.casefold()
        if language != "zh":
            return (
                "Which part best describes what happens?",
                [
                    "It will not power on or charge",
                    "It moves or navigates incorrectly",
                    "It runs but does not clean well",
                    "The dock is not working",
                    "The app cannot control the device",
                ],
            )

        if any(word in normalized for word in ("基站", "底座", "充电座")):
            return (
                "基站具体出现了哪种现象？",
                [
                    "机器找不到基站或无法回充",
                    "基站不能集尘，垃圾还在机器里",
                    "基站不出水或不清洗拖布",
                    "基站没有通电或指示灯不亮",
                ],
            )
        if any(word in normalized for word in ("app", "手机", "连接", "网络")):
            return (
                "手机端具体卡在哪一步？",
                [
                    "App 找不到设备或设备显示离线",
                    "设备能联网，但 App 指令没有反应",
                    "更换 Wi-Fi 后无法重新连接",
                    "账号登录或设备绑定失败",
                ],
            )
        if any(word in normalized for word in ("拖布", "拖地", "水箱", "水")):
            return (
                "拖地或水路问题更接近下面哪一种？",
                [
                    "拖布是干的，机器没有出水",
                    "基站不清洗拖布或污水不回收",
                    "拖完后地面有很多水",
                    "拖布无法升降或安装异常",
                ],
            )
        if any(word in normalized for word in ("扫", "吸", "灰", "垃圾", "清洁")):
            return (
                "清洁时最明显的现象是什么？",
                [
                    "机器正常运行，但灰尘和垃圾吸不干净",
                    "主刷或边刷不转，并伴随提示",
                    "清扫路线混乱、漏扫或重复清扫",
                    "运行时声音突然变大或有异响",
                ],
            )
        return (
            "请先选择最接近的现象，我会继续缩小问题范围：",
            [
                "设备无法开机、充电或很快没电",
                "设备移动异常、卡住或地图混乱",
                "设备能运行，但清洁效果明显变差",
                "基站的充电、集尘或水路功能异常",
                "手机 App 无法连接或控制设备",
            ],
        )

    @staticmethod
    def _human_review_message(language: str) -> str:
        return (
            "已为你转接人工专员。" if language == "zh" else "A support specialist will assist you."
        )

    @staticmethod
    def _step_message(language: str, model: str, instruction: str) -> str:
        if language == "zh":
            return f"我已识别设备为 {model}。先做一项安全检查：{instruction} 完成后请告诉我结果。"
        return (
            f"I identified the device as {model}. Please try one safe check first: "
            f"{instruction} Tell me what happens afterward."
        )
