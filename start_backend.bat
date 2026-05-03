@echo off
echo ========================================
echo   代码逻辑拓扑图工具 - 启动后端服务
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/3] 安装依赖...
pip install -r requirements.txt -q

echo [3/3] 启动FastAPI服务...
echo.
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python run.py
