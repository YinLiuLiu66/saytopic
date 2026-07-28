# SayTopic — Codex 项目规则

## 项目定位

使用用户名管理浏览器录音，并支持可选图片关联与二维码声纹明信片打印。

## 运行与验证

```bash
# 后端（端口 8000）
cd backend && uv run uvicorn main:app --port 8000

# 前端（端口 5173）
cd frontend && pnpm dev --host 0.0.0.0

# 前端构建检查
cd frontend && pnpm build

# 后端录音归属与播放计数测试
cd backend && uv run python -m unittest test_stats.py
```

## 技术与目录

- 前端：Vue 3、Vite、vue-router、qrcode，源代码在 `frontend/src/`。
- 后端：FastAPI，入口在 `backend/main.py`；上传内容存入被 Git 忽略的 `backend/uploads/`。
- 用户与接口说明以 `README.md` 为准；实现细节以 `docs/开发文档.md` 为准。

## 不可变约定

- 后端使用 `8000`，前端使用 `5173`；前端经 Vite 将 `/api` 代理到 `http://localhost:8000`，请求使用相对路径。
- 音频上传文件名使用 UUID；浏览器优先使用 `audio/mp4`，上传后扩展名为 `.m4a`，也支持 `.webm`、`.ogg`、`.mp3`、`.wav`。
- 图片只接受 jpg/jpeg、png、webp，最大 10MB；关联图片使用音频同名基名。
- 播放页仅在每次访问的首次实际播放时计数；公开次数存入 `backend/uploads/stats.sqlite3`。
- 用户名是 1–40 字符的身份标签，保存在浏览器 `localStorage`；同名用户共享录音列表，不提供真实认证。
- 当前允许的跨域来源为 `http://localhost:5173` 和 `https://frp-off.com:23506`；新增域名时同步更新 FastAPI CORS 与 Vite `allowedHosts`。

## 变更边界

- 保持改动最小；不要顺手重构或清理无关代码。
- 变更接口、端口、文件格式、路由或上传规则时，同步更新 README、开发文档和本文件。
- 未经用户确认，不删除会话残留、分支、worktree 或上传文件。
