# ============================================
# StudySeatOps 前端镜像（多阶段构建）
# 阶段一：Node 环境编译 Vue 项目
# 阶段二：Nginx 托管静态产物
# ============================================

# ---------- 阶段一：构建 ----------
FROM node:22-alpine AS builder

WORKDIR /app

# 先复制依赖清单，利用 Docker 缓存层
COPY package.json package-lock.json ./
RUN npm ci

# 复制源码
COPY . .

# 接收构建参数：API 地址（Docker 部署时留空，走 nginx 反向代理）
ARG VITE_API_BASE=""
ENV VITE_API_BASE=${VITE_API_BASE}

# 构建生产产物
RUN npm run build

# ---------- 阶段二：运行 ----------
FROM nginx:1.27-alpine

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制产物到 Nginx 静态目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 声明服务端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
