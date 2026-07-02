# SayTopic — AI 项目规则

## 行为守则

**注意：** 以下守则偏向谨慎而非速度。对于琐碎任务可自行判断。

### 1. 先思考，后编码

**不要假设。不要隐藏困惑。呈现权衡。**

实现前：
- 明确陈述你的假设。不确定就问。
- 若存在多种解读，全部列出——不要默默选择。
- 若有更简单的方案，直接说出来。必要时提出反对。
- 若有不理解的地方，停下来。指出困惑所在。提问。

### 2. 简洁优先

**用最少的代码解决问题。不做臆测性开发。**

- 不多实现一个没要求的特性。
- 不为只使用一次的代码创建抽象。
- 不添加没要求的"灵活性"或"可配置性"。
- 不为不可能场景写错误处理。
- 如果写了 200 行但能用 50 行搞定，重写。

问自己："资深工程师会说这个过于复杂吗？" 如果是，简化。

### 3. 精准改动

**只动必须动的。只清理自己造成的混乱。**

编辑既有代码时：
- 不要"顺手改进"相邻的代码、注释或格式。
- 不要重构没坏的东西。
- 遵循现有风格，即使你更倾向另一种写法。
- 若发现无关的死代码，提一句——不要删除。

当你的改动造成遗留时：
- 移除因你的改动而不再使用的 import/变量/函数。
- 不要动已存在的死代码，除非被要求。

检验标准：每行改动都应能直接追溯到用户的请求。

### 4. 目标驱动执行

**定义成功标准。循环直至验证。**

将任务转化为可验证的目标：
- "加校验" → "为无效输入写测试，然后让它们通过"
- "修 bug" → "写一个可复现的测试，然后让它通过"
- "重构 X" → "确保重构前后测试均通过"

对于多步骤任务，概述简要计划：
```
1. [步骤] → 验证：[检查方式]
2. [步骤] → 验证：[检查方式]
3. [步骤] → 验证：[检查方式]
```

---

**这些守则生效的标志是：** diff 中不必要改动更少、因过度复杂而重写更少、疑问出现在实现之前而非犯错之后。

---

> 完整架构与组件规范见 `docs/开发文档.md`。

## 项目速览

在线录音 + 图片上传 + 二维码声纹打印：Vue 3 (Vite, :5173) ↔ FastAPI (Python, :8000)。

## 目录结构

```
backend/main.py        # FastAPI: POST /api/upload, POST /api/upload-image (可选 audio_filename 参数), GET /api/audio/{filename}, GET/HEAD /api/image/{filename}
backend/uploads/       # 录音和图片文件存储（gitignore，UUID 命名）
frontend/src/          # Vue 3 应用
  router/index.js      # / → HomeView, /play/:filename → PlayView, /upload-image/:audioFilename → ImageUploadView
  views/               # HomeView（录音+电脑拍照/扫码上传+轮询同步+QR+波形+打印）, PlayView（音频播放）, ImageUploadView（手机端图片上传）
  components/          # AudioRecorder（录音）, CameraCapture（电脑拍照）, ImageUploader（图片上传，仅手机端）, WaveformCanvas（Canvas）, QrCodeCard（音频QR+波形+打印）
  assets/              # global.css（CSS 变量/字体）
```

## 硬规则

- **后端端口** `8000`，**前端端口** `5173`，不得冲突
- **Vite 代理**：`/api` → `http://localhost:8000`，前端 fetch 用相对路径
- **录音格式**：优先 mp4（iOS 兼容），其次 webm/ogg
- **图片格式**：支持 jpg/jpeg、png、webp，最大 10MB
- **UUID 重命名**：录音和图片文件以 `uuid4().hex + 扩展名` 存入 `uploads/`
- **文件关联**：图片与音频一对一关联，文件名相同（扩展名不同）
- **CORS**：允许 `localhost:5173` 和公网域名（内网穿透时需添加穿透域名）

## 启动命令

```bash
# 后端
cd backend && uv run uvicorn main:app --port 8000

# 前端
cd frontend && npm run dev -- --host 0.0.0.0
```
