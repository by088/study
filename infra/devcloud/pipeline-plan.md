# DevCloud 流水线迁移说明（阶段二）

## 构建任务
1. 拉取代码
2. 后端安装依赖并运行 pytest
3. 前端安装依赖并执行 npm run build
4. 产物归档（前端 dist、后端镜像构建上下文）

## 部署任务（Test）
1. Docker build backend/frontend
2. docker compose up -d
3. 执行 smoke test：GET /healthz

## 流水线阶段建议
1. 代码检出
2. 单元测试
3. 接口测试
4. 构建镜像
5. 自动部署 Test
6. 手动审批
7. 部署 Prod

## 质量门禁
- pytest 全通过
- 覆盖率 >= 70%（后续接入 coverage）
- 关键 API 冒烟通过
