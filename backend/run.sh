#!/bin/bash

# 设置Python路径
export PYTHONPATH=/lzcapp/pkg/content/backend

# 创建必要的目录
mkdir -p uploads output models

# 启动FastAPI应用
cd /lzcapp/pkg/content/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
