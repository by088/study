# ============================================
# StudySeatOps 后端镜像
# 基于 Python 3.12，运行 FastAPI + Uvicorn
# ============================================

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖清单，利用 Docker 缓存层
# 只有 requirements.txt 变化时才重新安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用源码和测试代码
COPY app ./app
COPY tests ./tests

# 创建数据目录（用于 SQLite 持久化）
RUN mkdir -p /app/data

# 声明服务端口
EXPOSE 8001

# 启动命令：绑定 0.0.0.0 使容器外部可访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
