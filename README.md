# LLM--localchat-UI
安全，简单、快速的单机 Ollama / llama.cpp 前端代理界面，功能完整、防御到位、体验极佳
 
**单机版本地界面**

纯前端简洁界面（2025 年版）＋单文件 Python 安全代理，实现：
- 丝滑本地的聊天体验
- 安全（强制本机 + 自定义 API Key）
- 按需自动加载模型，内存常时几乎为 0
- 零 Docker、零 Node.js、零复杂配置
 
## 核心优势 

| 特性          | Llama-Swap-UI-Local         | Open WebUI / SillyTavern / Ollama WebUI |
| ----------- | --------------------------- | --------------------------------------- |
| 安全性         | 强制 127.0.0.1 + 自定义 API Key  | 大多默认开放局域网                               |
| 模型加载方式      | 按需启动，闲时 0 额外内存占用            | 常驻进程或手动 reload                          |
| 部署复杂度       | 主干为1 个 Python 文件 + 1 个 HTML | 通常需要 Docker + 多容器                       |
| 启动速度（首次使用）  | 自动后台加载，体验无缝                 | 需手动选择模型并重启                              |
| 流式输出 + 错误提示 | 原生流式 + 详细中文错误信息             | 部分方案卡顿或英文报错                             |

## 当前局限性 

| 功能                   | 是否支持 | 说明                                 |
|------------------------|----------|--------------------------------------|
| 多会话（多个聊天标签） | ❌       | 当前仅支持单会话，刷新即清空         |
| 历史记录持久化         | ❌       | 可通过右上角导出 Markdown 解决       |
| 角色卡/系统提示模板    | ❌       | 仅支持全局 System Prompt             |
| 模型管理可视化界面     | ❌       | 通过修改 config.yaml 管理            |
| 移动端完美适配         | ⚠️       | 可使用，但输入框和按钮稍小           |
| 插件/扩展生态          | ❌       | 完全没有，保持极简                   |

→ 适合人群：**追求极致界面与隐私的单人裸聊党、开发者、技术极客**  
→ 不适合人群：重度角色扮演、多会话、需要复杂角色卡的用户

## 安装与部署 

### 1. 克隆仓库
```bash
git clone https://github.com/yourname/llama-swap.git
cd llama-swap
```

### 2. 准备模型与 llama.cpp
- 编译或下载最新版 [llama.cpp](https://github.com/ggerganov/llama.cpp) 的 `llama-server`
- 推荐使用支持 `--health` 端点的版本（2025 年后的 master 都支持）
- 将可执行文件重命名为 `llama-server.exe`（Windows）或 `llama-server`（Linux/macOS）并放入项目根目录，或在 config.yaml 中指定完整路径

### 3. 创建 .env 文件（必须）
```env
PROXY_API_KEY=sk-your-custom-key-here-1234567890
```
> 长度建议 ≥ 32 位，随意填，越长越好

### 4. 编辑 config.yaml（必填）
```yaml
llama_server_path: "./llama-server"          # Windows 改成 "./llama-server.exe"
default_model: llama3.1:8b                    # 启动后自动加载的模型（可选）

default_args:
  - "--ctx-size"
  - "8192"
  - "--threads"
  - "12"

models:
  llama3.1:8b:
    path: "C:/Models/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf"
    args: ["--temp", "0.7"]

  gemma2-27b:
    path: "C:/Models/gemma-2-27b-it-Q6_K.gguf"
    args: ["--temp", "0.8", "--repeat-penalty", "1.1"]
 
```

### 5. 安装 Python 依赖
```bash
pip install flask requests pyyaml python-dotenv
```

### 6. 启动
```bash
python proxy1.py
```

看到类似输出即成功：
```
[*] Llama-Swap 安全代理已启动
    访问地址 → http://127.0.0.1:5206/chat
    当前 API Key → sk-yo****1234
[+] 正在预加载默认模型：llama3.1:8b
    等待模型加载...就绪!
```

### 7. 浏览器打开
http://127.0.0.1:5206/chat

在设置 → API Key 中填入你刚才设置的 `sk-...` 即可使用

## 安全注意事项（非常重要）

- 代理默认只监听 127.0.0.1，**任何情况下不要改为 0.0.0.0**
- API Key 一定设置且不要泄露
- 所有静态资源均通过代理提供，无跨域风险
- 支持局域网访问的方法：只改前端 BASE_API_URL 为内网 IP（不推荐）

## 贡献与 Star

如果你觉得好用，请给颗 Star，这是对作者最大的鼓励。

也欢迎提交 Issue 或 PR：
- 新增多会话功能（规划中）
- 历史记录本地存储
- 模型管理页面
- 移动端优化

## License

MIT © 2025 Your Name
 
