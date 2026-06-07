# banksys Dockerfile
# 使用 Python 3.11 slim 镜像,国内可切换基础镜像源

FROM python:3.11-slim

LABEL app="banksys"

WORKDIR /app

# Python 需能找到 app 包(代码在 /app/app/)
ENV PYTHONPATH=/app

# 系统依赖(Streamlit 可能需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 复制应用代码与数据
COPY app/ ./app/
COPY model/ ./model/
COPY data/ ./data/

# 构建时训练模型(避免容器启动后手动训练)
RUN python model/train.py

# 容器内固定端口 8501
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

# 启动 Streamlit
ENTRYPOINT ["streamlit", "run", "app/main.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
