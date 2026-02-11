#!/bin/bash
# Railway 部署脚本

set -e  # 遇到错误立即退出

echo "=================================================="
echo "   E-Business - Railway 部署脚本"
echo "=================================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Railway CLI
echo -e "\n${YELLOW}步骤 1/6: 检查 Railway CLI...${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI 未安装${NC}"
    echo "正在安装 Railway CLI..."
    npm install -g @railway/cli
    echo -e "${GREEN}✓ Railway CLI 安装完成${NC}"
else
    echo -e "${GREEN}✓ Railway CLI 已安装${NC}"
fi

# 步骤 2: 登录 Railway
echo -e "\n${YELLOW}步骤 2/6: 登录 Railway...${NC}"
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "请提供您的 Railway Token："
    echo "1. 访问 https://railway.app/"
    echo "2. 登录后进入 Settings → API Tokens"
    echo "3. 创建新 Token 并复制"
    echo ""
    read -p "请粘贴您的 Railway Token: " RAILWAY_TOKEN

    if [ -z "$RAILWAY_TOKEN" ]; then
        echo -e "${RED}错误: 未提供 Token${NC}"
        exit 1
    fi

    railway login --token "$RAILWAY_TOKEN"
else
    echo -e "${GREEN}✓ 已使用环境变量中的 Token${NC}"
    railway login --token "$RAILWAY_TOKEN"
fi

# 步骤 3: 初始化项目
echo -e "\n${YELLOW}步骤 3/6: 初始化 Railway 项目...${NC}"
if [ -f ".railway/project.json" ]; then
    echo -e "${GREEN}✓ Railway 项目已存在${NC}"
else
    railway init
    echo -e "${GREEN}✓ 项目初始化完成${NC}"
fi

# 步骤 4: 设置环境变量
echo -e "\n${YELLOW}步骤 4/6: 配置环境变量...${NC}"

echo "请输入您的 API Keys:"

# DeepSeek API Key
read -p "DeepSeek API Key: " DEEPSEEK_KEY
if [ -n "$DEEPSEEK_KEY" ]; then
    railway variables set DEEPSEEK_API_KEY="$DEEPSEEK_KEY"
    echo -e "${GREEN}✓ DEEPSEEK_API_KEY 已设置${NC}"
fi

# LangSmith API Key
read -p "LangSmith API Key (格式: lsv2_pt_...): " LANGSMITH_KEY
if [ -n "$LANGSMITH_KEY" ]; then
    railway variables set LANGCHAIN_API_KEY="$LANGSMITH_KEY"
    echo -e "${GREEN}✓ LANGCHAIN_API_KEY 已设置${NC}"
fi

# LangSmith 追踪
railway variables set LANGCHAIN_TRACING_V2=true
railway variables set LANGCHAIN_PROJECT=e-business
echo -e "${GREEN}✓ LangSmith 配置已设置${NC}"

# 其他配置
railway variables set PYTHON_VERSION=3.11
echo -e "${GREEN}✓ Python 版本已设置${NC}"

# 步骤 5: 添加 PostgreSQL（如果需要）
echo -e "\n${YELLOW}步骤 5/6: 添加数据库服务...${NC}"
read -p "是否需要在 Railway 上添加 PostgreSQL 数据库？(y/n): " ADD_DB

if [ "$ADD_DB" = "y" ]; then
    railway add postgresql
    echo -e "${GREEN}✓ PostgreSQL 已添加${NC}"

    # 获取数据库 URL
    echo ""
    echo "数据库将自动创建 DATABASE_URL 环境变量"
    echo "您可以在 Railway Dashboard 中查看连接信息"
fi

# 步骤 6: 部署
echo -e "\n${YELLOW}步骤 6/6: 部署到 Railway...${NC}"
railway up

# 等待部署完成
echo -e "\n${YELLOW}等待部署完成...${NC}"
sleep 5

# 获取部署信息
echo -e "\n${GREEN}=================================================="
echo "   部署完成！"
echo "==================================================${NC}"

# 获取项目 URL
echo -e "\n${YELLOW}项目信息:${NC}"
railway status

echo -e "\n${YELLOW}访问您的应用:${NC}"
railway domain

echo -e "\n${YELLOW}查看日志:${NC}"
echo "railway logs"

echo -e "\n${YELLOW}打开 Dashboard:${NC}"
echo "railway open"

echo -e "\n${GREEN}=================================================="
echo "   LangSmith 监控配置:"
echo "==================================================${NC}"
echo "✓ LangSmith 追踪已启用"
echo "✓ 项目名称: e-business"
echo ""
echo "访问 https://smith.langchain.com 查看追踪记录"

echo -e "\n${GREEN}部署成功！${NC}"
