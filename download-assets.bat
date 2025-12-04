@echo off
chcp 65001 >nul
echo ========================================
echo   Chat Page 资源文件下载脚本
echo ========================================
echo.

REM 创建 assets 目录
if not exist "assets" (
    mkdir assets
    echo [✓] 创建 assets 目录
) else (
    echo [✓] assets 目录已存在
)

echo.
echo [1/5] 下载 marked.min.js...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js', 'assets\marked.min.js')" 2>nul
if exist "assets\marked.min.js" (echo [✓] marked.min.js 下载完成) else (echo [✗] marked.min.js 下载失败)

echo.
echo [2/5] 下载 highlight.min.js...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/highlight.min.js', 'assets\highlight.min.js')" 2>nul
if exist "assets\highlight.min.js" (echo [✓] highlight.min.js 下载完成) else (echo [✗] highlight.min.js 下载失败)

echo.
echo [3/5] 下载 purify.min.js (DOMPurify)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js', 'assets\purify.min.js')" 2>nul
if exist "assets\purify.min.js" (echo [✓] purify.min.js 下载完成) else (echo [✗] purify.min.js 下载失败)

echo.
echo [4/5] 下载 github.min.css...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css', 'assets\github.min.css')" 2>nul
if exist "assets\github.min.css" (echo [✓] github.min.css 下载完成) else (echo [✗] github.min.css 下载失败)

echo.
echo [5/5] 下载 github-dark.min.css...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css', 'assets\github-dark.min.css')" 2>nul
if exist "assets\github-dark.min.css" (echo [✓] github-dark.min.css 下载完成) else (echo [✗] github-dark.min.css 下载失败)

echo.
echo ========================================
echo   所有资源文件下载完成！
echo ========================================
echo.
echo 请现在运行: python proxy.py
echo 访问地址: http://127.0.0.1:5206/chat
echo.
pause
