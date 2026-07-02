# SayTopic

在线录音 + 图片上传 + 二维码声纹打印工具：在浏览器中录音，手机扫码上传图片，生成二维码和波形图，通过新窗口预览 148mm×100mm 明信片并打印。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + vue-router + qrcode |
| 后端 | FastAPI + uvicorn |
| 包管理 | npm (前端) / uv (后端) |

## 快速开始

```bash
# 后端
cd backend
uv run uvicorn main:app --port 8000

# 前端（新终端）
cd frontend
npm run dev -- --host 0.0.0.0
```

## 目录结构

```
saytopic/
├── backend/
│   ├── main.py          # FastAPI 入口（上传 / 音频服务 / 图片服务 / CORS）
│   ├── pyproject.toml   # Python 依赖
│   └── uploads/         # 录音和图片文件存储（gitignore）
├── frontend/
│   ├── src/
│   │   ├── main.js      # 入口（挂载 Router）
│   │   ├── router/      # / → Home, /play/:filename → Play, /upload-image/:audioFilename → ImageUpload
│   │   ├── views/       # HomeView, PlayView, ImageUploadView
│   │   ├── components/  # AudioRecorder, CameraCapture, ImageUploader, WaveformCanvas, QrCodeCard
│   │   └── assets/      # global.css
│   └── vite.config.js   # Vue 插件 + /api 代理
└── docs/
    └── 开发文档.md       # 完整架构与开发计划
```

## 开发环境 URL

| 用途 | URL |
|------|-----|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| 音频上传接口 | POST /api/upload |
| 图片上传接口 | POST /api/upload-image |
| 音频文件 | GET /api/audio/{filename} |
| 图片文件 | GET /api/image/{filename} |
| 播放页面 | http://localhost:5173/play/{filename} |
| 图片上传页面 | http://localhost:5173/upload-image/{audioFilename} |

## 内网穿透

使用樱花 frp 等工具穿透前端端口（5173），Vite 会自动代理 `/api` 到后端。需在 `backend/main.py` 的 CORS 配置中添加穿透域名。
