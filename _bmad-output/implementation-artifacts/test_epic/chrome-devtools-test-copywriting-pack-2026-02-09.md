# Chrome DevTools 测试文案包（Copywriting）

日期: 2026-02-09  
目标: 验证文案生成功能在浏览器端完整可用，且不再出现 `DeepSeek API key is required`

## 1. 测试前置

1. 启动后端: `cd backend && poetry run uvicorn app.main:app --reload --port 8000`
2. 启动前端: `npm run dev`
3. 打开 `http://localhost:3000`
4. 打开 Chrome DevTools (`F12`)
5. 在 `Network` 勾选 `Preserve log`
6. 过滤关键请求: `copywriting`、`socket.io`

## 2. 测试输入文案（可直接复制）

### 套件 A（香水）
- productName: `Midnight Suede`
- features:
  - `前调黑胡椒与佛手柑`
  - `中调鸢尾与玫瑰木`
  - `后调檀香与麝香留香12小时`
- brandGuidelines: `高端、克制、电影感，避免绝对化夸张词。`

### 套件 B（智能手表）
- productName: `PulseTrack X1`
- features:
  - `双频GPS精准定位`
  - `24小时心率与血氧监测`
  - `7天续航，30分钟快充`
- brandGuidelines: `科技感、直接、强调可量化收益。`

### 套件 C（咖啡机）
- productName: `Barista Mini Pro`
- features:
  - `9档研磨粗细`
  - `20bar稳定萃取`
  - `60秒自动奶泡`
- brandGuidelines: `生活方式表达，强调早晨高效场景。`

## 3. DevTools 执行步骤

1. 登录后进入首页。
2. 使用任一套件触发文案生成。
3. 检查 `POST /api/v1/copywriting/generate` 返回 `202`。
4. 检查 `socket.io` 已连接并持续收消息。
5. 页面出现阶段流: `plan -> draft -> critique -> finalize`。
6. 页面出现最终文案，且没有 API key 报错。

## 4. 验收标准

1. `copywriting/generate` 返回 `202`。
2. WebSocket 连接稳定，无连续重连。
3. 阶段流完整，至少 4 个阶段更新。
4. 最终文案成功展示。
5. Console 中无 `WORKFLOW_FAILED`，无 `DeepSeek API key is required`。

## 5. 失败时记录模板

- 时间:
- 输入套件: A / B / C
- API 状态码:
- socket.io 状态:
- 页面错误文案:
- Console 关键报错:
- 截图文件名:
