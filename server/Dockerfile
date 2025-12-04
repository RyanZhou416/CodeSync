# 使用官方轻量 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 环境变量：防止生成 .pyc 文件，保证日志实时打印
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装依赖
# 注意：server.py 用到了 fastapi 和 uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# 复制当前目录下的所有文件到容器的 /app
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]