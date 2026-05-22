# StudySeatOps（阶段二重构仓库）

## 1. 项目定位
本仓库用于完成《自习座位预约系统》阶段二要求：
- 全量用户故事定义
- 超过一半核心功能实现
- DevCloud DevOps 全流程落地

## 2. 当前已完成
- 新仓库骨架（backend/frontend/docs/infra）
- 阶段二行动看板：`docs/phase2-plan.md`
- 全量用户故事：`docs/user-stories.md`
- 后端 FastAPI 分层骨架（配置、模型、规则、API、测试）
- 前端 Vue3 + Vite 骨架（学生端/管理端路由与 API 封装）
- Dockerfile 与 docker-compose 基础编排

## 3. 本地启动
### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker compose up --build
```

## 4. 下一步开发（按阶段二优先级）
1. 认证与 RBAC
2. 自习室/座位查询
3. 预约/取消/签到主流程
4. 违约自动处理任务
5. 管理端 CRUD
6. 测试覆盖率门禁
7. DevCloud 构建与部署流水线
