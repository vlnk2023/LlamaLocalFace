@echo off
chcp 65001 >nul
title Llama-Swap 模型代理服务器

echo ========================================================
echo               Llama-Swap 一键启动工具
echo ========================================================
 

:: 2. 检查并安装依赖库
echo [*] 正在检查依赖环境...
python -c "import flask, yaml, requests, dotenv" >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] 发现缺失依赖库，正在自动安装...
    pip install flask pyyaml requests python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败！请检查网络。
        pause
        exit /b
    )
    echo [+] 依赖安装完成！
) else (
    echo [+] 环境检查通过。
)

:: 3. 检查配置文件
if not exist config.yaml (
    echo [WARN] 未找到 config.yaml，正在生成默认配置...
    (
    echo llama_server_path: "llamacpp/llama-server.exe"
    echo default_args:
    echo   - "-c"
    echo   - "8192"
    echo   - "-ngl"
    echo   - "99"
    echo   - "--host"
    echo   - "127.0.0.1"
    echo models:
    echo   test:
    echo     path: "model/model_Q8_0.gguf"
    ) > config.yaml
    echo [+] 已生成默认 config.yaml，请记得修改里面的路径！
)

:: 4. 启动代理服务
echo.
echo [*] 正在启动代理服务器...
echo [*] 确保 llama-server.exe 和模型文件路径正确
echo.
python proxy.py

pause