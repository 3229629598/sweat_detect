@echo off
chcp 65001 >nul
echo ==============================
echo 正在激活 conda 环境 wx_backend...
echo ==============================

:: 激活 conda 环境（如果 conda 已在系统PATH中）
call conda activate wx_backend

:: 如果 conda 不在系统PATH，用下面这一行，替换成你的 conda 路径
:: call D:\miniconda3\Scripts\activate.bat wx_backend

if %errorlevel% neq 0 (
    echo 错误：conda 环境 wx_backend 激活失败！
    pause
    exit /b 1
)

echo ==============================
echo 检查项目依赖...
echo ==============================
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo 警告：部分依赖安装失败，请手动检查 requirements.txt
) else (
    echo 依赖检查/安装完成！
)

echo ==============================
echo conda 环境激活成功！
echo 正在启动 Django 服务...
echo ==============================

:: 切换到脚本所在目录（项目根目录）
cd /d %~dp0

:: 启动 Django 服务
python manage.py runserver 0.0.0.0:8000

:: 保持窗口打开
pause