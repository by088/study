# DevCloud 可直接执行配置清单（阶段二）

> 适用目录：`StudySeatOps/backend` 与 `StudySeatOps/frontend`

## 1. 编译构建任务（Build）

### 后端构建命令
```bash
cd StudySeatOps/backend
python3 -m pip install -r requirements.txt
python3 -m pytest
```

### 前端构建命令
```bash
cd StudySeatOps/frontend
npm install
npm run build
```

## 2. 部署任务（Test 环境）

### 部署命令
```bash
cd StudySeatOps
docker compose down
docker compose up -d --build
```

### 冒烟检查命令
```bash
curl http://127.0.0.1:8001/healthz
```

## 3. 定时任务（可在 DevCloud 定时执行）

### 预约前15分钟提醒
```bash
cd StudySeatOps/backend
python3 -m scripts.run_jobs --mode before15
```

### 预约后10分钟提醒
```bash
cd StudySeatOps/backend
python3 -m scripts.run_jobs --mode after10
```

### 预约后15分钟违约扫描
```bash
cd StudySeatOps/backend
python3 -m scripts.run_jobs --mode defaults
```

## 4. 流水线节点建议顺序
1. 拉取代码
2. 后端依赖安装与单测
3. 前端构建
4. Docker 镜像构建
5. 自动部署到 Test
6. 冒烟测试
7. 人工审批
8. 部署到 Prod

## 5. 质量门禁建议
- `pytest` 失败则流水线中断
- 冒烟检查失败则禁止进入审批节点
- 覆盖率门禁（下一步接入）：`pytest --cov` >= 70%
