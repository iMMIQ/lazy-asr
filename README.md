# Lazy ASR

一个基于Silero VAD语音活动检测和多种ASR引擎的自动分段转录工具，支持前后端分离架构和插件化ASR算法。

## 功能特点

- 🎯 **Silero VAD语音活动检测**: 自动检测音频中的语音段，提高转录准确率
- 🔧 **插件化ASR引擎**: 支持多种ASR算法，易于扩展
- 🌐 **前后端分离**: React前端 + FastAPI后端
- 🐳 **容器化部署**: 使用Docker和docker-compose一键部署
- 📝 **SRT字幕生成**: 自动生成标准SRT字幕文件

## 支持的ASR引擎

1. **Faster-Whisper**: 基于Whisper的高性能ASR引擎
2. **Qwen-ASR**: 阿里通义千问ASR服务

## 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/                 # FastAPI应用
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   ├── utils/           # 工具函数
│   │   └── main.py          # 应用入口
│   ├── plugins/             # ASR插件
│   ├── requirements.txt     # Python依赖
│   └── Dockerfile           # 后端Docker配置
├── frontend/                # 前端应用 (React + TypeScript + Vite)
│   ├── public/              # 静态资源
│   ├── src/                 # React源码 (TypeScript)
│   ├── package.json         # Node.js依赖
│   └── Dockerfile           # 前端Docker配置
├── uploads/                 # 上传文件目录
├── output/                  # 输出文件目录
├── docker-compose.yml       # Docker编排配置
└── README.md                # 项目说明文档
```

## 快速开始

### 环境要求

- Docker & docker-compose
- Python 3.10+ (本地开发)
- Node.js 18+ (本地开发)

### 使用Docker部署

1. 克隆项目:
   ```bash
   git clone <repository-url>
   cd lazy-asr
   ```

2. 设置环境变量:
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 编辑.env文件，添加必要的API密钥
   nano .env
   ```

3. 构建并启动服务:
   ```bash
   sudo docker compose up --build
   ```

4. 访问应用:
   - 前端界面: http://localhost:3000
   - API文档: http://localhost:8000/docs

### 本地开发

#### 后端开发

1. 安装依赖:
   ```bash
   cd backend
   uv sync
   ```

2. 运行后端服务:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

#### 前端开发

1. 安装依赖:
   ```bash
   cd frontend
   npm install
   ```

2. 运行前端开发服务器:
   ```bash
   npm run dev
   ```

3. 运行测试:
   ```bash
   npm run test
   ```

4. 构建生产版本:
   ```bash
   npm run build
   ```

## API接口

### 获取可用ASR插件
```http
GET /api/v1/asr/plugins
```

### 处理音频文件
```http
POST /api/v1/asr/process
Content-Type: multipart/form-data

audio_file: <音频文件>
asr_method: <ASR方法>
```

### 下载SRT文件
```http
GET /api/v1/asr/download/<文件路径>
```

## 插件开发

要添加新的ASR插件，请继承`ASRPlugin`基类并实现以下方法:

```python
from backend.plugins.base import ASRPlugin

class MyASRPlugin(ASRPlugin):
    def __init__(self):
        super().__init__("my-asr-plugin")
    
    async def transcribe(self, audio_file_path: str) -> str:
        # 实现转录逻辑
        pass
    
    async def transcribe_segments(self, segments: List[Dict]) -> List[Dict]:
        # 实现分段转录逻辑
        pass
```

然后在`backend/plugins/__init__.py`中注册插件:
```python
from .my_asr_plugin import MyASRPlugin
plugin_manager.register_plugin(MyASRPlugin())
```

## 配置说明

### 环境变量

- `QWEN_ASR_API_KEY`: 阿里通义千问ASR服务API密钥
- `UPLOAD_DIR`: 上传文件目录 (默认: uploads)
- `OUTPUT_DIR`: 输出文件目录 (默认: output)
