from dataclasses import dataclass

from mova_support.domain import RiskLevel, SafetyDecision


@dataclass(frozen=True)
class SafetyRule:
    code: str
    keywords: tuple[str, ...]
    message_zh: str
    message_en: str


CRITICAL_RULES = (
    SafetyRule(
        code="thermal_risk",
        keywords=(
            "发烫",
            "烫手",
            "过热",
            "温度很高",
            "异常发热",
            "overheating",
            "overheated",
            "too hot to touch",
            "extremely hot",
        ),
        message_zh=(
            "请立即停止使用并断开电源，将设备放在通风、远离易燃物的位置自然冷却。"
            "不要继续充电、运行或拆机；客服专员将介入处理。"
        ),
        message_en=(
            "Stop using the device and disconnect power. Let it cool naturally "
            "in a ventilated area away from flammable materials. Do not charge, "
            "run, or open it; a specialist will assist you."
        ),
    ),
    SafetyRule(
        code="battery_fire_risk",
        keywords=(
            "冒烟",
            "烧焦",
            "起火",
            "电池膨胀",
            "smoke",
            "burning",
            "swollen battery",
            "battery is swollen",
        ),
        message_zh="请立即停止使用并断开电源；不要充电、拆机或继续测试。客服专员将尽快介入。",
        message_en=(
            "Stop using the device and disconnect power immediately. "
            "Do not charge, open, or continue testing it. A specialist will assist you."
        ),
    ),
    SafetyRule(
        code="electric_water_risk",
        keywords=("漏电", "水进电源", "严重漏水", "electric shock", "water near power"),
        message_zh="请勿触碰积水中的设备或电源。确保安全后关闭电源，并等待客服专员处理。",
        message_en=(
            "Do not touch the device or power source near water. "
            "Turn off power only when safe and wait for specialist assistance."
        ),
    ),
    SafetyRule(
        code="injury_or_damage",
        keywords=("受伤", "财产损失", "咬到宠物", "injury", "property damage", "hurt my pet"),
        message_zh="此问题需要专员立即处理。请停止使用设备并保留现场照片和相关信息。",
        message_en=(
            "This issue requires specialist review. Stop using the device "
            "and preserve relevant photos and information."
        ),
    ),
)


def evaluate_safety(message: str, locale: str) -> SafetyDecision:
    normalized = message.casefold()
    matched = [
        rule for rule in CRITICAL_RULES if any(k.casefold() in normalized for k in rule.keywords)
    ]
    if not matched:
        return SafetyDecision(risk=RiskLevel.LOW, requires_human=False)

    rule = matched[0]
    return SafetyDecision(
        risk=RiskLevel.CRITICAL,
        requires_human=True,
        matched_rules=[item.code for item in matched],
        user_message=rule.message_zh if locale.lower().startswith("zh") else rule.message_en,
    )
