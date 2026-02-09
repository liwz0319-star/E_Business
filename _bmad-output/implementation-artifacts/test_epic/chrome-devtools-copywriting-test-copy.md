# Chrome DevTools 测试文案（Copywriting 回归）

**生成日期**: 2026-02-09  
**目标问题**: 异步工作流报错 `DeepSeek API key is required`  
**适用范围**: 前端 `localhost:3000` + 后端 `localhost:8000`

## 1. 测试前准备

1. 启动后端：`cd backend && poetry run uvicorn app.main:app --reload --port 8000`
2. 启动前端：`npm run dev`
3. 打开 Chrome，访问 `http://localhost:3000`
4. 打开 DevTools（`F12`）
5. Network 勾选 `Preserve log`，过滤关键字：`copywriting`、`socket.io`

## 2. 可直接复制的测试输入文案

### 文案 A（高端香水）
- Product Name: `Midnight Suede`
- Features:
  - `前调黑胡椒与佛手柑`
  - `中调鸢尾与玫瑰木`
  - `后调檀香与麝香留香12小时`
- Brand Guidelines: `高端、克制、具电影感，避免夸张词。`

### 文案 B（智能手表）
- Product Name: `PulseTrack X1`
- Features:
  - `双频GPS精准定位`
  - `24小时心率与血氧监测`
  - `7天续航+30分钟快充`
- Brand Guidelines: `科技感、直接、可量化收益导向。`

### 文案 C（咖啡机）
- Product Name: `Barista Mini Pro`
- Features:
  - `9档研磨粗细`
  - `20bar稳定萃取`
  - `60秒自动奶泡`
- Brand Guidelines: `生活方式导向，强调早晨场景与效率。`

## 3. Chrome DevTools 执行步骤（主路径）

1. 注册或登录后进入首页。
2. 触发一次文案生成（卡片或输入框均可）。
3. 在 Network 中确认 `POST /api/v1/copywriting/generate` 返回 `202`。
4. 在 Network 中确认 `socket.io` 连接成功（`101` 或轮询升级成功）。
5. 在页面观察流式阶段输出：`plan -> draft -> critique -> finalize`。
6. 最终页面出现完整 `final copy`，且无 `DeepSeek API key is required`。

## 4. 验收标准

1. API 首次请求成功：`/copywriting/generate` 返回 `202`。
2. WebSocket 保持连接，不频繁断开重连。
3. 工作流阶段完整，至少出现 4 个阶段更新。
4. 最终文案返回成功，页面无红色错误提示。
5. Console 无 `WORKFLOW_FAILED` 且无 `DeepSeek API key is required`。

## 5. 异常回归检查（负向）

1. 人为将 `DEEPSEEK_API_KEY` 置空后重启后端。
2. 重复主路径步骤。
3. 预期：
   - 前端收到错误事件并展示失败态；
   - 错误信息为配置缺失相关；
   - 恢复 key 后再次执行可恢复成功。

## 6. 结果记录模板

- 执行人：
- 执行时间：
- 输入文案：A / B / C
- API 状态码：
- WebSocket 状态：
- 阶段流是否完整：是 / 否
- 最终结果：通过 / 失败
- 失败截图与 console 摘要：
