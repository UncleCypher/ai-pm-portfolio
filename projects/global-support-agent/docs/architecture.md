# 系统架构

当前 MVP 使用同步 FastAPI 服务和显式诊断服务。规则引擎先于知识诊断执行，危险场景不会进入自助排查。

```text
HTTP API
  -> DiagnosisService
      -> Safety Engine
      -> Symptom Detection
      -> Versioned Knowledge
      -> Hypothesis Ranking
      -> Fake Support Tools / future production adapters
```

下一阶段将把 `DiagnosisService` 迁移为有状态图编排，并增加 PostgreSQL 会话存储、知识导入、设备授权和真实工具适配器。领域模型不依赖这些基础设施。

