import pytest

from mova_support.application import DiagnosisService
from mova_support.domain import DeviceIdentity, DiagnosisOutcome, DiagnosisRequest


@pytest.mark.parametrize(
    "message,locale,country",
    [
        ("设备冒烟了", "zh-CN", "CN"),
        ("电池膨胀还很烫", "zh-CN", "CN"),
        ("There is smoke and a burning smell", "en-US", "US"),
        ("The battery is swollen", "en-US", "US"),
        ("水进电源插座了", "zh-CN", "CN"),
        ("机器运行一会就非常发烫", "zh-CN", "CN"),
        ("The device is too hot to touch", "en-US", "US"),
    ],
)
def test_known_critical_cases_are_never_self_served(
    message: str,
    locale: str,
    country: str,
) -> None:
    response = DiagnosisService().diagnose(
        DiagnosisRequest(
            message=message,
            locale=locale,
            country=country,
            device=DeviceIdentity(model="P50 Ultra"),
        )
    )

    assert response.outcome == DiagnosisOutcome.HUMAN_REVIEW
    assert response.safety.requires_human is True
