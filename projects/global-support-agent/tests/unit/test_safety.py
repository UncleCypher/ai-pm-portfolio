from mova_support.diagnostics.safety import evaluate_safety
from mova_support.domain import RiskLevel


def test_battery_smoke_requires_human_review() -> None:
    result = evaluate_safety("机器突然冒烟，还有烧焦味", "zh-CN")

    assert result.requires_human is True
    assert result.risk == RiskLevel.CRITICAL
    assert "battery_fire_risk" in result.matched_rules


def test_normal_fault_is_low_risk() -> None:
    result = evaluate_safety("机器无法回充", "zh-CN")

    assert result.requires_human is False
    assert result.risk == RiskLevel.LOW


def test_overheating_requires_immediate_human_review() -> None:
    result = evaluate_safety("机器运行十分钟后特别发烫，已经烫手了", "zh-CN")

    assert result.requires_human is True
    assert result.risk == RiskLevel.CRITICAL
    assert "thermal_risk" in result.matched_rules
    assert result.user_message is not None
    assert "停止使用" in result.user_message
