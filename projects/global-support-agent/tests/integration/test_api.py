from fastapi.testclient import TestClient

from mova_support.api import app

client = TestClient(app)


def test_chinese_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "全球智能售后客服" in response.text
    assert "未受 MOVA 委托" in response.text
    assert "开始诊断" in response.text


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_diagnose_endpoint() -> None:
    response = client.post(
        "/api/v1/diagnose",
        json={
            "message": "My robot is offline and cannot connect to Wi-Fi",
            "locale": "en-US",
            "country": "US",
            "device": {"model": "P50 Ultra", "firmware_version": "1.0.0"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "self_service"
    assert body["symptoms"][0]["code"] == "offline"
    assert body["next_step"]["step_id"] == "check_wifi"


def test_unknown_problem_returns_guided_choices() -> None:
    response = client.post(
        "/api/v1/diagnose",
        json={
            "message": "基站最近不太正常",
            "locale": "zh-CN",
            "country": "CN",
            "device": {"model": "P50 Ultra"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "need_more_evidence"
    assert body["clarifying_question"] == "基站具体出现了哪种现象？"
    assert body["suggested_replies"]


def test_model_config_does_not_expose_api_key() -> None:
    response = client.get("/api/v1/model-config")

    assert response.status_code == 200
    body = response.json()
    assert "api_key" not in body
    assert body["provider"] in {"local", "deepseek"}


def test_deepseek_key_can_be_tested_and_enabled(monkeypatch) -> None:
    class ModelResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"language":"zh","intent":"device_fault",'
                                '"sentiment":"neutral","symptom_codes":["offline"],'
                                '"normalized_problem":"设备离线","missing_information":[],'
                                '"out_of_taxonomy":false,"proposed_symptom_label":null,'
                                '"confidence":0.9}'
                            )
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer sk-test-secret"
        return ModelResponse()

    monkeypatch.setattr("mova_support.nlu.provider.httpx.post", fake_post)
    response = client.put(
        "/api/v1/model-config",
        json={"api_key": "sk-test-secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "deepseek"
    assert body["connected"] is True
    assert body["api_key_configured"] is True
    assert "sk-test-secret" not in response.text


def test_model_config_rejects_invalid_key_without_exposing_it(monkeypatch) -> None:
    import httpx

    def failing_post(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr("mova_support.nlu.provider.httpx.post", failing_post)
    response = client.put(
        "/api/v1/model-config",
        json={"api_key": "sk-invalid-secret"},
    )

    assert response.status_code == 502
    assert "sk-invalid-secret" not in response.text
