# Findings & Decisions

## Requirements
修复E2E测试中发现的"DeepSeek API key is required"错误：
- ✅ 后端配置文件正确（backend/.env包含API key）
- ✅ 直接curl测试成功
- ✅ 测试脚本可以正常加载配置
- ❌ 前端WebSocket异步工作流失败

**目标：**使前端触发的异步工作流能够正确加载环境变量

## Research Findings

### 根本原因（Gemini深度调研 + Claude代码探索）

**环境加载脆弱性 (Environment Loading Fragility)**

原代码仅依赖单一路径来加载.env文件：
```python
# backend/app/core/config.py (第30行)
env_file=[
    str(Path(__file__).parent.parent.parent / ".env"),  # 项目根目录
    ".env",
    "../.env"
]
```

**问题分析：**
- `Path(__file__).parent.parent.parent / ".env"` 解析为项目根目录的`.env`
- 但实际配置文件位于 `backend/.env`
- 在不同执行上下文中（uvicorn、IDE终端、独立命令行），CWD可能不同
- pydantic-settings可能找不到文件，**静默失败**（赋值为None）

**为什么测试脚本可以工作？**
- 独立测试脚本的CWD是`backend`目录
- 相对路径".env"可以匹配到backend/.env
- pydantic的fallback机制生效

**为什么异步任务失败？**
- uvicorn启动的进程CWD可能不同
- @lru_cache()在模块首次加载时缓存配置
- 如果那时配置未正确加载，后续访问也会失败

### 已完成的修复

**main.py - 启动时强制验证（第28-60行）**
- ✅ 显示详细的诊断信息（CWD、配置路径、API key状态）
- ✅ 配置缺失时直接崩溃并报错（Fail Fast）
- ✅ 不允许服务在错误状态下启动

### 待完成的核心修复

**config.py - 多级路径策略（第29-33行）**

当前代码：
```python
env_file=[
    str(Path(__file__).parent.parent.parent / ".env"),
    ".env",
    "../.env"
]
```

修复为：
```python
env_file=[
    # 标准开发环境路径（新增）
    str(Path(__file__).parent.parent.parent / "backend" / ".env"),
    # 项目根目录（生产环境）
    str(Path(__file__).parent.parent.parent / ".env"),
    # 相对路径作为fallback
    "backend/.env",
    ".env",
    "../.env"
]
```

**为什么这样修复？**
1. 明确包含`backend/.env`路径，解决开发环境的标准位置
2. 保留所有fallback路径确保向后兼容
3. 支持多种执行上下文（VSCode终端、独立命令行、Docker等）

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 修改config.py的env_file路径 | 解决根本原因：明确包含backend/.env |
| 保留main.py的启动验证 | 作为双重保险，Fail Fast原则 |
| 分步实施 | 先修复核心问题，再增强错误处理 |
| 重启后端验证 | 清除缓存，确保配置重新加载 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 环境变量在不同上下文中加载不一致 | 采用多级路径策略 |
| 配置静默失败导致调试困难 | main.py添加启动强制验证 |

## Resources
**关键文件路径：**
- `backend/app/core/config.py` (第29-33行) - 待修复
- `backend/app/main.py` (第28-60行) - 已完成
- `backend/.env` - 配置文件位置
- `F:\AAA Work\AIproject\E_Business\_bmad-output\implementation-artifacts\plan2.md` - 详细文档

**执行命令：**
```powershell
# 重启后端
Get-Process python | Stop-Process -Force -ErrorAction SilentlyContinue
cd "f:\AAA Work\AIproject\E_Business\backend"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Visual/Browser Findings
**启动日志预期输出（成功）：**
```
==================================================
BACKEND STARTUP CHECK
==================================================
Checking .env paths:
 - CWD: f:\AAA Work\AIproject\E_Business\backend
 - Config File: f:\AAA Work\AIproject\E_Business\backend\app\core\config.py
 - Expected .env: f:\AAA Work\AIproject\E_Business\backend\.env
 - Exists? True
DeepSeek API Key Status: ✅ LOADED
Key Value (Masked): sk-98afb2...ef8c
==================================================
```

**E2E测试成功标志：**
- ✅ 不再出现"DeepSeek API key is required"错误
- ✅ 看到4阶段工作流执行（plan → draft → critique → finalize）
- ✅ WebSocket实时更新正常显示

---
*基于Gemini深度调研和Claude代码探索的综合分析*
