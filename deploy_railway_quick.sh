#!/bin/bash
# Railway 快速部署脚本

echo "=================================================="
echo "   E-Business - Railway 快速部署"
echo "=================================================="

# 检查参数
if [ -z "$1" ]; then
    echo ""
    echo "使用方法: ./deploy_railway_quick.sh <RAILWAY_TOKEN>"
    echo ""
    echo "参数说明:"
    echo "  RAILWAY_TOKEN - 您的 Railway API Token"
    echo ""
    echo "获取 Token:"
    echo "  1. 访问 https://railway.app/"
    echo "  2. 登录后进入 Settings → API Tokens"
    echo "  3. 创建新 Token 并复制"
    echo ""
    exit 1
fi

RAILWAY_TOKEN=$1

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}步骤 1/5: 登录 Railway...${NC}"
railway login --token "$RAILWAY_TOKEN"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 登录成功${NC}"
else
    echo "登录失败，请检查 Token"
    exit 1
fi

echo -e "\n${YELLOW}步骤 2/5: 初始化项目...${NC}"
railway init --name e-business
echo -e "${GREEN}✓ 项目初始化完成${NC}"

echo -e "\n${YELLOW}步骤 3/5: 设置环境变量...${NC}"

# 收集 API Keys
echo ""
echo "请输入您的 API Keys:"
echo ""

read -p "DeepSeek API Key: " DEEPSEEK_KEY
if [ -n "$DEEPSEEK_KEY" ]; then
    railway variables set DEEPSEEK_API_KEY="$DEEPSEEK_KEY"
    echo -e "${GREEN}✓ DEEPSEEK_API_KEY 已设置${NC}"
fi

read -p "LangSmith API Key (格式: lsv2_pt_...): " LANGSMITH_KEY
if [ -n "$LANGSMITH_KEY" ]; then
    railway variables set LANGCHAIN_API_KEY="$LANGSMITH_KEY"
    echo -e "${GREEN}✓ LANGCHAIN_API_KEY 已设置${NC}"
fi

# 设置 LangSmith 配置
railway variables set LANGCHAIN_TRACING_V2=true
railway variables set LANGCHAIN_PROJECT=e-business
echo -e "${GREEN}✓ LangSmith 配置已设置${NC}"

# 设置 Python 版本
railway variables set PYTHON_VERSION=3.11
echo -e "${GREEN}✓ Python 版本已设置为 3.11${NC}"

echo -e "\n${YELLOW}步骤 4/5: 添加数据库（可选）...${NC}"
read -p "是否添加 PostgreSQL 数据库？(y/n): " ADD_DB

if [ "$ADD_DB" = "y" ]; then
    railway add postgresql
    echo -e "${GREEN}✓ PostgreSQL 已添加${NC}"
    echo ""
    echo "注意：Railway 会自动创建 DATABASE_URL 环境变量"
fi

echo -e "\n${YELLOW}步骤 5/5: 部署应用...${NC}"
railway up

echo -e "\n${YELLOW}等待部署完成...${NC}"
sleep 5

echo -e "\n${GREEN}=================================================="
echo "   部署完成！"
echo "==================================================${NC}"

echo -e "\n${YELLOW}项目信息:${NC}"
railway status

echo -e "\n${YELLOW}应用 URL:${NC}"
railway domain

echo -e "\n${YELLOW}查看实时日志:${NC}"
echo "  railway logs -f"

echo -e "\n${YELLOW}打开 Railway Dashboard:${NC}"
echo "  railway open"

echo -e "\n${GREEN}=================================================="
echo "   LangSmith 监控"
echo "==================================================${NC}"
echo "✓ LangSmith 追踪已启用"
echo "✓ 项目名称: e-business"
echo ""
echo "访问: https://smith.langchain.com/projects"

echo -e "\n${GREEN}🎉 部署成功！${NC}"
