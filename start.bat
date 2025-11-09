@echo off
REM Windows 启动脚本

echo 🚀 启动 Dify 知识库检索增强 API...

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  警告: .env 文件不存在!
    echo 📝 正在从 .env.example 创建 .env...
    copy .env.example .env
    echo ✅ .env 文件已创建,请编辑配置后再次运行此脚本
    pause
    exit /b 1
)

REM 检查 Python
python --version
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt

REM 启动服务
echo 🎯 启动服务...
python main.py

pause
