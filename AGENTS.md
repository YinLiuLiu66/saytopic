# SayTopic — Codex 项目规则

## 项目定位

共享电脑完成录音、可选图片关联与二维码声纹明信片打印；用户在手机端以用户名累计自己听过的不同录音数量。

## 运行与验证

```bash
# 后端（端口 8000）
cd backend && uv run uvicorn main:app --port 8000

# 前端（端口 5173）
cd frontend && pnpm dev --host 0.0.0.0

# 前端构建检查
cd frontend && pnpm build

# 后端数据统计测试
cd backend && uv run python -m unittest test_stats.py
```

## 技术与目录

- 前端：Vue 3、Vite、vue-router、qrcode，源代码在 `frontend/src/`。
- 后端：FastAPI，入口在 `backend/main.py`；上传内容存入被 Git 忽略的 `backend/uploads/`。
- 用户与接口说明以 `README.md` 为准；实现细节以 `docs/开发文档.md` 为准；Debian 上线与运维以 `docs/部署文档.md` 为准。

## 不可变约定

- 后端使用 `8000`，前端使用 `5173`；前端经 Vite 将 `/api` 代理到 `http://localhost:8000`，请求使用相对路径。
- 麦克风和摄像头依赖浏览器安全上下文：同机开发可用 `http://localhost:5173`，局域网或公网访问必须使用 HTTPS。
- 音频上传文件名使用 UUID；浏览器优先使用 `audio/mp4`，上传后扩展名为 `.m4a`，也支持 `.webm`、`.ogg`、`.mp3`、`.wav`。
- 图片只接受 jpg/jpeg、png、webp，最大 10MB；关联图片使用音频同名基名。
- 当前允许的跨域来源为 `http://localhost:5173` 和 `https://frp-off.com:23506`；新增域名时同步更新 FastAPI CORS 与 Vite `allowedHosts`。

## 业务约定

- 完整业务合同见 `docs/开发文档.md` 的“业务流程”。
- 共享电脑录音时不输入或保存用户名；打印窗口关闭后只重置浏览器页面，服务器文件继续保留。
- 手机播放前必须有用户名；用户名保存在手机 `localStorage`、区分大小写、无密码，同名共享数据。
- 个人已听数量按“用户名 + 录音文件名”去重；系统不维护录音归属列表或单条录音累计播放次数。
- `/mine` 是个人统计与凭证图片页面；播放页提供入口，不提供录音浏览列表。
- 正式活动前需经用户确认后清空服务器测试数据；不得在开发过程中自动删除。

## 变更边界

- 保持改动最小；不要顺手重构或清理无关代码。
- 变更接口、端口、文件格式、路由或上传规则时，同步更新 README、开发文档和本文件。
- 未经用户确认，不删除会话残留、分支、worktree 或上传文件。
