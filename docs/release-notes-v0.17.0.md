## API 版本化

- 正式接口：`GET /v1/health`、`POST /v1/query`
- 旧路径 `/health`、`/query` 保留为兼容别名（不出现在 OpenAPI 文档中）
- OpenAPI 完善：请求/响应模型、字段约束、401/429 说明；文档在 `/docs`

```bash
curl -sS -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"ETag 和 Last-Modified 哪个更精确？","ctx_tokens":300}'
```

## 工程状态

- 测试 65 个，覆盖率 **90%**（CI 门槛 80%）
- Docker：镜像非 root + HEALTHCHECK，CI 真实构建并打一次请求已通过
- 依赖锁、数据快照、五分钟教程齐备

## 距离 1.0.0

只剩「论文投出」一项（工程侧已完成）。