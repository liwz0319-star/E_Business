# 📊 LangSmith 使用教程

## 🎯 LangSmith 是什么？

LangSmith 是 LangChain 提供的开发者平台，用于：
- 🔍 **追踪** - 记录所有 LLM 调用
- 🐛 **调试** - 查看详细的输入输出
- 📈 **监控** - 分析性能和成本
- 🧪 **测试** - 批量测试不同提示词
- 📊 **可视化** - 图形化展示工作流

---

## 🚀 快速开始

### 步骤 1: 访问 LangSmith

1. 打开浏览器，访问：**https://smith.langchain.com**
2. 点击右上角 **"Log In"** 或 **"Sign Up"**
3. 使用账号登录（如果还没有账号，注册一个，是免费的）

### 步骤 2: 找到您的项目

登录后，您会看到项目列表：

```
┌─────────────────────────────────────┐
│  📁 Projects                    │
│                                 │
│  ┌──────────────────────────┐    │
│  │ e-business ◀──── 您的项目│    │
│  └──────────────────────────┘    │
│                                 │
│  [Create New Project]            │
└─────────────────────────────────────┘
```

点击 **"e-business"** 项目进入详情。

---

## 📋 LangSmith 界面介绍

进入项目后，您会看到几个主要标签页：

### 1. **Runs** 标签页（追踪记录）⭐

这是最重要的标签页，显示所有的 LLM 调用记录。

#### 界面布局

```
┌──────────────────────────────────────────────────┐
│  🔍 Search runs...                  [Filter] │
├──────────────────────────────────────────────────┤
│  ▼ Time range: Last 24 hours ▼          │
│                                          │
│  ┌──────────────────────────────────────┐   │
│  │ Run #1234    Feb 11, 2026      │   │
│  │ ✅ Success   2.3s   $0.004     │   │
│  │                                   │   │
│  │ 🤖 CopywritingAgent                │   │
│  │                                  │   │
│  │ Plan → Draft → Critique → Finalize  │   │
│  │ [View Details]                     │   │
│  └──────────────────────────────────────┘   │
│                                          │
│  [Load More]                           │
└──────────────────────────────────────────────────┘
```

#### 每条记录显示的信息

| 信息 | 说明 |
|------|------|
| **Run #** | 追行编号（唯一标识）|
| **状态** | ✅ Success / ❌ Error / ⏱️ Running |
| **时间** | 执行时间（秒）|
| **成本** | Token 使用量和估算成本 |
| **工作流** | Agent 类型（CopywritingAgent/ImageAgent）|

---

### 2. 点击查看详细信息

点击任意一条记录，进入详细页面：

```
┌────────────────────────────────────────────┐
│  Run #1234 - CopywritingAgent      │
│  ✅ Success   2.345s    $0.004   │
├────────────────────────────────────────────┤
│                                          │
│  📊 Timeline                          │
│  ┌──────────────────────────────────┐    │
│  │ 1. plan_node (0.8s)         │    │
│  │    Input: product_name, features │    │
│  │    Output: {...}               │    │
│  │                                │    │
│  │ 2. draft_node (1.2s)        │    │
│  │    Input: {...}                 │    │
│  │    Output: {...}                │    │
│  │                                │    │
│  │ 3. critique_node (0.9s)      │    │
│  │    Input: {...}                 │    │
│  │    Output: {...}                │    │
│  │                                │    │
│  │ 4. finalize_node (0.5s)      │    │
│  │    Input: {...}                 │    │
│  │    Output: final_copy           │    │
│  └──────────────────────────────────┘    │
│                                          │
│  📝 Input/Output                      │
│  ┌──────────────────────────────────┐    │
│  │ 📥 Inputs:                      │    │
│  │ product_name: "智能手表"         │    │
│  │ features: [...]                   │    │
│  │                                  │    │
│  │ 📤 Outputs:                     │    │
│  │ final_copy: "..."               │    │
│  └──────────────────────────────────┘    │
│                                          │
│  [🔍 Back to Runs]                   │
└────────────────────────────────────────────┘
```

#### 详细信息包含

##### **Timeline（时间线）**
- 显示工作流中每个节点的执行顺序
- 每个节点的时间、输入、输出
- 可以点击展开查看详细信息

##### **Inputs（输入）**
- 完整的请求参数
- 提示词内容
- 配置参数

##### **Outputs（输出）**
- LLM 的完整响应
- 生成的文本内容
- Token 使用统计

##### **Metadata（元数据）**
- 执行时间
- 模型名称
- Temperature、Top-P 等参数

---

### 3. **Monitoring** 标签页

实时监控应用性能：

```
┌────────────────────────────────────────┐
│  📈 Latency (ms)                 │
│  ▁▃▄█▆█                         │
│  2.3s  ◄─ 平均延迟             │
│                                    │
│  📊 Total Runs                      │
│  1,234  ◄─ 总运行次数             │
│                                    │
│  💰 Total Cost                       │
│  $4.56  ◄─ 总成本               │
└────────────────────────────────────────┘
```

---

### 4. **Testing** 标签页

用于批量测试和评估（高级功能）：

- 🧪 创建测试数据集
- 🔄 批量运行测试
- 📊 评估结果对比
- 📈 性能趋势分析

---

## 🔍 实际操作示例

### 场景 1: 触发一个 API 请求

```bash
# 调用文案生成 API
curl -X POST https://e-business-api.onrender.com/api/v1/copywriting/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "智能手表",
    "features": ["GPS定位", "心率监测"]
  }'
```

### 场景 2: 在 LangSmith 查看追踪

1. **访问** https://smith.langchain.com
2. **选择项目** "e-business"
3. **刷新页面**（按 F5 或点击刷新按钮）
4. **看到新的追踪记录**（通常在顶部）

---

## 🎯 如何使用追踪信息

### 1. 调试提示词

**问题**：生成质量不好

**操作**：
1. 在 Runs 中找到对应记录
2. 点击查看详情
3. 查看 **Inputs** 标签，查看发送给 LLM 的提示词
4. 查看 **Outputs** 标签，查看 LLM 的响应
5. 分析问题并修改提示词

**示例**：
```
❌ 不好：
Input: "写个文案"
Output: "好的文案"

✅ 好：
Input: "为智能手表创作营销文案，突出GPS和心率监测功能"
Output: "【智能手表】您的24小时健康管家..."
```

---

### 2. 优化性能

**问题**：响应太慢

**操作**：
1. 查看 Timeline 中的节点时间
2. 找到最慢的节点
3. 检查是否可以优化提示词减少 token
4. 或考虑缓存常见请求

**示例**：
```
plan_node: 0.8s  ✅ 快速
draft_node: 5.2s  ⚠️ 太慢
critique_node: 1.1s  ✅ 正常
```

---

### 3. 监控成本

**操作**：
1. 查看 **Monitoring** 标签
2. 查看 **Total Cost**（总成本）
3. 分析哪些请求最贵
4. 考虑优化或添加缓存

**成本优化建议**：
- 减少提示词长度
- 使用更便宜的模型
- 缓存常见响应
- 限制最大 token 数

---

### 4. 分析工作流

**您的应用使用 LangGraph**，可以在 LangSmith 看到完整的工作流：

```
┌──────────────────────────────────┐
│  🤖 CopywritingAgent        │
│                            │
│  ┌────┐  ┌─────┐  ┌───────┐│
│  │Plan│→│Draft│→│Critique││
│  └────┘  └─────┘  └───────┘│
│              ↓                │
│         ┌──────────┐          │
│         │Finalize  │          │
│         └──────────┘          │
│              ↓                │
│         ✅ Complete          │
└──────────────────────────────────┘
```

**好处**：
- 清楚看到每个阶段的输入输出
- 识别瓶颈节点
- 理解完整的数据流

---

## 🎨 高级功能

### 1. 添加标签和注释

在代码中为追踪添加自定义标签：

```python
from langsmith import traceable

@traceable(name="custom_copywriting")
async def generate_copywriting(product_name: str, features: list):
    # 您的代码
    pass
```

在 LangSmith 中会显示：
- 自定义名称
- 标签分类
- 便于筛选

---

### 2. 添加反馈

在 LangSmith UI 中：
1. 打开一条 Run 详情
2. 点击 **"Add Feedback"** 按钮
3. 添加评分（1-5 星）
4. 添加评论

**用途**：
- 记录哪些结果好/坏
- 后续批量评估
- 训练数据收集

---

### 3. 共享和导出

**共享 Run**：
1. 打开 Run 详情
2. 点击 **"Share"** 按钮
3. 复制分享链接
4. 发给团队成员查看

**导出数据**：
1. 在 Runs 页面点击 **"Export"**
2. 选择格式（CSV/JSON）
3. 下载用于分析

---

## 🔧 过滤和搜索

### 按时间筛选

```
Time Range: [Last 24 hours ▼]
选项:
- Last 15 minutes
- Last 1 hour
- Last 24 hours
- Last 7 days
- Last 30 days
- Custom range
```

### 按状态筛选

```
Filter: [All Runs ▼]
选项:
- All Runs
- Success only
- Error only
- With Feedback
```

### 搜索功能

```
🔍 Search runs...
可以搜索:
- Run ID
- 提示词内容
- 输出内容关键词
- 标签名称
```

---

## 📊 实际使用示例

### 示例 1: 调试文案生成失败

**问题**：客户报告文案生成失败

**步骤**：
1. 访问 LangSmith → e-business 项目
2. 点击 **Runs** 标签
3. 选择 **Error only** 筛选
4. 找到红色的失败记录
5. 点击查看详情
6. 查看 **Timeline** 找到失败节点
7. 查看 **Error Message** 了解错误原因

**可能看到的错误**：
```
❌ Error in finalize_node:
   "HTTPClientError: DeepSeek API timeout"
   → 检查 API Key 或网络连接
```

---

### 示例 2: 优化响应时间

**问题**：平均响应时间 5 秒，太慢

**步骤**：
1. 查看 **Monitoring** 标签，确认平均延迟
2. 点击 **Runs** 标签，按时间排序
3. 查看最慢的几次记录
4. 分析 Timeline，找到慢的节点
5. 查看节点的输入（prompt 是否太长）
6. 优化代码或提示词

**发现**：
```
draft_node: 平均 4.2s
原因: prompt 太长（2000+ tokens）
优化: 简化 prompt，减少到 500 tokens
结果: draft_node 降至 1.8s ✅
```

---

### 示例 3: A/B 测试不同提示词

**目标**：测试哪个提示词效果更好

**步骤**：
1. 准备两个版本的 prompt
2. 分别触发 API 请求
3. 在 LangSmith 查看两次 Run
4. 对比输出质量
5. 记录反馈（1-5 星）
6. 选择更好的版本

---

## 🎯 最佳实践

### 1. 命名规范

为项目和服务取清晰的名字：
- ✅ "e-business-copywriting"
- ✅ "e-business-image-gen"
- ❌ "test"（太模糊）

### 2. 环境分离

为不同环境使用不同项目：
- **e-business-dev** - 开发环境
- **e-business-staging** - 测试环境
- **e-business-prod** - 生产环境

### 3. 定期检查

养成习惯定期查看：
- 每天：检查错误和异常
- 每周：分析性能趋势
- 每月：评估成本和优化

### 4. 使用反馈

记录反馈帮助：
- 识别常见问题模式
- 收集好的示例
- 训练评估模型

---

## 🆘 常见问题

### Q: 看不到任何追踪记录

**A**:
1. 检查 `/api/v1/debug/langsmith` 是否显示 `enabled: true`
2. 确认 `LANGCHAIN_API_KEY` 正确
3. 确认网络可以访问 `api.smith.langchain.com`
4. 触发一个新的 API 请求
5. 刷新 LangSmith 页面

### Q: 追踪有延迟

**A**:
- 正常延迟：1-5 秒
- 如果超过 10 秒，检查网络或 API 问题
- LangSmith 使用异步上传，不会阻塞应用

### Q: 只看到部分工作流

**A**:
- 检查是否所有节点都调用了 langsmith 追踪
- LangGraph 默认会追踪所有节点
- 检查代码中是否禁用了追踪

---

## 📚 延伸阅读

- [LangSmith 官方文档](https://docs.smith.langchain.com)
- [LangChain 追踪指南](https://python.langchain.com/docs/tracing)
- [成本优化指南](https://docs.smith.langchain.com/pricing)
- [项目文档](./LANGSMITH_GUIDE.md)

---

## 🎉 开始使用吧！

现在您已经知道如何：

1. ✅ 访问 LangSmith
2. ✅ 查看追踪记录
3. ✅ 分析详细执行过程
4. ✅ 调试和优化应用
5. ✅ 监控性能和成本

**立即打开**：https://smith.langchain.com/projects

选择 **"e-business"** 项目开始探索！🚀
