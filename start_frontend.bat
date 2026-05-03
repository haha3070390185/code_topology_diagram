@echo off
echo ========================================
echo   代码逻辑拓扑图工具 - 启动前端服务
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo [2/3] 安装依赖...
call npm install

if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo [3/3] 启动Vue3开发服务器...
echo.
echo 前端地址: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

call npm run dev
