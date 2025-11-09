#!/bin/bash

# 启动脚本

echo "🚀 启动 Dify 知识库检索增强 API..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在!"
    echo "📝 正在从 .env.example 创建 .env..."
    cp .env.example .env
    echo "✅ .env 文件已创建,请编辑配置后再次运行此脚本"
    exit 1
fi

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "📌 Python 版本: $python_version"

# 检查依赖
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  未检测到虚拟环境"
    echo "💡 建议创建虚拟环境: python -m venv venv"
fi

# 安装依赖
echo "📦 检查依赖..."
pip install -r requirements.txt --quiet

# 启动服务
echo "🎯 启动服务..."
python main.py
