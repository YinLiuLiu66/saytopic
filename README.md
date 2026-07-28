# SayTopic

在线录音 + 图片上传 + 二维码声纹打印工具：使用用户名创建和查看自己的录音，手机扫码上传图片，生成二维码和波形图，通过新窗口预览 148mm×100mm 明信片并打印；扫码播放页公开显示录音被聆听的次数。

**GitHub 仓库：** https://github.com/YinLiuLiu66/saytopic

## 获取代码

```bash
git clone https://github.com/YinLiuLiu66/saytopic.git
cd saytopic
```

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + vue-router + qrcode |
| 后端 | FastAPI + uvicorn |
| 包管理 | pnpm (前端) / uv (后端) |

## 快速开始

```bash
# 后端
cd backend
uv run uvicorn main:app --port 8000

# 前端（新终端）
cd frontend
pnpm dev --host 0.0.0.0
```

## 目录结构

```
saytopic/
├── backend/
│   ├── main.py          # FastAPI 入口（上传 / 用户录音 / 播放计数 / 文件服务 / CORS）
│   ├── pyproject.toml   # Python 依赖
│   └── uploads/         # 录音、图片和归属/计数数据库（gitignore）
├── frontend/
│   ├── src/
│   │   ├── main.js      # 入口（挂载 Router）
│   │   ├── router/      # 首页、我的录音、播放页和手机图片上传页
│   │   ├── views/       # HomeView, MyRecordingsView, PlayView, ImageUploadView
│   │   ├── components/  # AudioRecorder, CameraCapture, WaveformCanvas, QrCodeCard
│   │   └── assets/      # global.css
│   └── vite.config.js   # Vue 插件 + /api 代理
└── docs/
    └── 开发文档.md       # 完整架构、接口与实现说明
```

## 开发环境 URL

| 用途 | URL |
|------|-----|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| 音频上传接口 | POST /api/upload |
| 图片上传接口 | POST /api/upload-image |
| 音频文件 | GET /api/audio/{filename} |
| 播放次数 | GET /api/audio/{filename}/stats |
| 记录播放 | POST /api/audio/{filename}/play |
| 用户录音 | GET /api/recordings?owner_name={username} |
| 图片文件 | GET /api/image/{filename} |
| 播放页面 | http://localhost:5173/play/{filename} |
| 图片上传页面 | http://localhost:5173/upload-image/{audioFilename} |
| 我的录音 | http://localhost:5173/mine |

## 用户名身份

首页输入的用户名保存在当前浏览器中，新录音会关联该用户名；“我的录音”页面按用户名展示录音和播放次数。该功能不包含密码或真实认证，任何人输入相同用户名都会看到同一份录音列表。

## 内网穿透

使用樱花 frp 等工具穿透前端端口（5173），Vite 会自动代理 `/api` 到后端。新增穿透域名时，需同时更新 `backend/main.py` 的 CORS 配置和 `frontend/vite.config.js` 的 `allowedHosts`。
