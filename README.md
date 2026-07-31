# SayTopic

共享电脑录音 + 可选图片上传 + 二维码声纹明信片打印工具；用户扫码播放录音，并通过手机用户名累计自己听过的不同录音数量。

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
│   ├── main.py          # FastAPI 入口（上传 / 已听统计 / 文件服务 / CORS）
│   ├── pyproject.toml   # Python 依赖
│   └── uploads/         # 录音、图片和已听统计数据库（gitignore）
├── frontend/
│   ├── src/
│   │   ├── main.js      # 入口（挂载 Router）
│   │   ├── router/      # 创作页、个人统计、播放页和手机图片上传页
│   │   ├── views/       # HomeView, MyStatsView, PlayView, ImageUploadView
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
| 已听统计 | GET /api/listening-stats?username={username} |
| 记录已听 | POST /api/audio/{filename}/play?username={username} |
| 图片文件 | GET /api/image/{filename} |
| 播放页面 | http://localhost:5173/play/{filename} |
| 图片上传页面 | http://localhost:5173/upload-image/{audioFilename} |
| 我的统计 | http://localhost:5173/mine |

## 用户名身份

用户名只在手机播放页和个人统计页使用，并保存在该手机的 `localStorage`。用户名区分大小写，不包含密码或真实认证；任何设备输入相同用户名都会共享同一份已听数据。同一用户名重复播放同一录音只计一条。

## 共享电脑流程

共享电脑无需输入用户名。打印对话框关闭后，网页会清空本次录音和图片并回到初始状态，但服务器文件继续保留，确保明信片二维码长期可用。

## 内网穿透

使用樱花 frp 等工具穿透前端端口（5173），Vite 会自动代理 `/api` 到后端。新增穿透域名时，需同时更新 `backend/main.py` 的 CORS 配置和 `frontend/vite.config.js` 的 `allowedHosts`。

浏览器只允许网页在安全上下文中访问麦克风和摄像头：同一台电脑可使用 `http://localhost:5173`，通过局域网 IP 或公网访问时必须使用 HTTPS，否则录音或拍照会提示无法获取权限。
