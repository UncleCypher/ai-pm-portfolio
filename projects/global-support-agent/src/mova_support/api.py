import os
from importlib.resources import files
from threading import RLock

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ValidationError

from mova_support.application import DiagnosisService
from mova_support.domain import DiagnosisRequest, DiagnosisResponse
from mova_support.nlu import (
    OpenAICompatibleConfig,
    OpenAICompatibleUnderstandingProvider,
    ResilientUnderstandingProvider,
    RuntimeUnderstandingProvider,
)

app = FastAPI(
    title="全球智能售后客服 Agent（以 MOVA 为案例）",
    version="0.1.0",
    description=(
        "面向全球智能家电售后场景的可审计诊断 Agent 概念验证。"
        "本项目以 MOVA 产品场景为公开案例研究，不代表 MOVA 官方产品或合作项目。"
    ),
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    },
)


def build_understanding_provider() -> tuple[ResilientUnderstandingProvider, str, str]:
    provider = os.getenv("MODEL_PROVIDER", "fake").lower()
    api_key = os.getenv("MODEL_API_KEY", "")
    model = os.getenv("MODEL_NAME", "")
    if provider == "openai_compatible" and api_key and model:
        primary = OpenAICompatibleUnderstandingProvider(
            OpenAICompatibleConfig(
                base_url=os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1"),
                api_key=api_key,
                model=model,
                timeout_seconds=float(os.getenv("MODEL_TIMEOUT_SECONDS", "15")),
            )
        )
        return ResilientUnderstandingProvider(primary=primary), provider, model
    return ResilientUnderstandingProvider(primary=None), "local", "local-rules"


initial_provider, initial_provider_name, initial_model_name = build_understanding_provider()
runtime_understanding = RuntimeUnderstandingProvider(initial_provider)
service = DiagnosisService(understanding=runtime_understanding)
_model_config_lock = RLock()
_model_config = {
    "provider": "deepseek" if initial_provider_name == "openai_compatible" else "local",
    "model": initial_model_name,
    "connected": initial_provider_name == "openai_compatible",
    "api_key_configured": initial_provider_name == "openai_compatible",
}


class DeepSeekConfigRequest(BaseModel):
    api_key: str = Field(min_length=8, max_length=512)
    model: str = Field(default="deepseek-chat", min_length=1, max_length=100)
    base_url: str = Field(default="https://api.deepseek.com", pattern=r"^https://")
    timeout_seconds: float = Field(default=15, ge=3, le=60)


class ModelConfigResponse(BaseModel):
    provider: str
    model: str
    connected: bool
    api_key_configured: bool


def current_model_config() -> ModelConfigResponse:
    with _model_config_lock:
        return ModelConfigResponse.model_validate(_model_config)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    html = files("mova_support").joinpath("web/index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/model-config", response_model=ModelConfigResponse)
def get_model_config() -> ModelConfigResponse:
    """Return connection state only; secrets are deliberately never returned."""
    return current_model_config()


@app.put("/api/v1/model-config", response_model=ModelConfigResponse)
def configure_deepseek(config: DeepSeekConfigRequest) -> ModelConfigResponse:
    candidate = OpenAICompatibleUnderstandingProvider(
        OpenAICompatibleConfig(
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            timeout_seconds=config.timeout_seconds,
        )
    )
    try:
        candidate.understand("设备离线，App 无法连接", "zh-CN", "P50 Ultra")
    except (httpx.HTTPError, KeyError, TypeError, ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=502,
            detail="DeepSeek 连接验证失败，请检查 API Key、网络或模型名称。",
        ) from exc

    runtime_understanding.replace(ResilientUnderstandingProvider(primary=candidate))
    with _model_config_lock:
        _model_config.update(
            provider="deepseek",
            model=config.model,
            connected=True,
            api_key_configured=True,
        )
    return current_model_config()


@app.delete("/api/v1/model-config", response_model=ModelConfigResponse)
def disable_remote_model() -> ModelConfigResponse:
    runtime_understanding.replace(ResilientUnderstandingProvider(primary=None))
    with _model_config_lock:
        _model_config.update(
            provider="local",
            model="local-rules",
            connected=False,
            api_key_configured=False,
        )
    return current_model_config()


@app.post("/api/v1/diagnose", response_model=DiagnosisResponse)
def diagnose(request: DiagnosisRequest) -> DiagnosisResponse:
    return service.diagnose(request)
