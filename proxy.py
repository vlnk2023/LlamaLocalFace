import subprocess
import time
import os
import sys
import signal

# 移除原本的直接 import，改为带错误处理的 import
try:
    import yaml
    import requests
    from flask import Flask, request, Response, stream_with_context, send_file, send_from_directory
    from dotenv import load_dotenv
except ImportError as e:
    print("\n[!] 错误: 缺少必要的 Python 库")
    print(f"    缺失模块: {e.name}")
    print("    请在命令行运行以下命令安装:")
    print("    pip install pyyaml flask requests python-dotenv")
    # 移除 input() 以防止在非交互式环境中出现 EOFError
    sys.exit(1)

# --- 安全配置 ---
CONFIG_FILE = 'config.yaml'
LLAMA_SERVER_PORT = 8083   # 内部 llama-server 运行的端口
PROXY_PORT = 5206         # 对外暴露的端口
BIND_HOST = '127.0.0.1'   # 关键安全设置：只允许本机访问，禁止局域网访问
# 自定义一个 API Key，客户端必须带上这个 Key 才能访问
# 你可以修改这里，或者在环境变量里设置 PROXY_API_KEY
# 加载 .env 文件
load_dotenv()

PROXY_API_KEY = os.environ.get("PROXY_API_KEY")
if PROXY_API_KEY is None:
    print("\n[!] 错误: 环境变量 PROXY_API_KEY 未设置。")
    print("    请在 .env 文件中设置 PROXY_API_KEY，或者设置环境变量。")
    sys.exit(1)

app = Flask(__name__)
current_process = None
current_model_name = None

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"错误: 找不到配置文件 {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def check_auth():
    """验证请求头中的 Authorization: Bearer sk-..."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    # 提取 Token
    try:
        token = auth_header.split(" ")[1]
        return token == PROXY_API_KEY
    except IndexError:
        return False

def is_server_ready():
    """检查 llama-server 是否已经启动并准备好接收请求"""
    try:
        response = requests.get(f"http://127.0.0.1:{LLAMA_SERVER_PORT}/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def stop_current_server():
    global current_process, current_model_name
    if current_process:
        print(f"[-] 正在停止模型: {current_model_name} (PID: {current_process.pid})")
        current_process.terminate()
        try:
            current_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            current_process.kill()
        current_process = None
        current_model_name = None
        time.sleep(1) # 等待端口释放

def start_model(model_key, config):
    global current_process, current_model_name
    
    if model_key not in config['models']:
        return False, f"Model '{model_key}' not found in config."

    # 如果已经在运行这个模型，直接返回
    if current_model_name == model_key and current_process and current_process.poll() is None:
        return True, "Already running"

    # 停止旧模型
    stop_current_server()

    # 准备启动命令
    model_conf = config['models'][model_key]
    exe_path = config.get('llama_server_path')
    
    # 检查模型文件是否存在
    model_path = model_conf['path']
    if not os.path.exists(model_path):
        error_msg = f"模型文件不存在: {model_path}"
        print(f"\n[!] {error_msg}")
        return False, error_msg
    
    # 构建命令
    cmd = [exe_path, "--port", str(LLAMA_SERVER_PORT), "-m", model_conf['path']]
    
    # 添加全局默认参数
    if 'default_args' in config:
        for arg in config['default_args']:
            cmd.append(arg)
            
    # 添加模型特定参数
    if 'args' in model_conf:
        for arg in model_conf['args']:
            cmd.append(arg)

    print(f"[+] 正在启动模型: {model_key}")
    print(f"    命令: {' '.join(cmd)}")

    try:
        # 启动子进程，捕获输出用于诊断
        current_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        current_model_name = model_key
        
        # 等待服务器就绪
        print("    等待模型加载...", end="", flush=True)
        max_retries = 100  # 100秒
        
        for i in range(max_retries):
            # 检查进程是否崩溃
            if current_process.poll() is not None:
                print("\n[FATAL] llama-server 进程异常退出!")
                print("\n=== 错误输出 ===")
                output = current_process.stdout.read()
                print(output)
                print("================\n")
                current_process = None
                current_model_name = None
                return False, "llama-server 进程崩溃，请检查上面的错误输出"
            
            # 检查服务器是否就绪
            if is_server_ready():
                print(" 就绪!")
                return True, "Started"
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        # 超时
        print("\n[!] 加载超时 (5分钟)!")
        stop_current_server()
        return False, "模型加载超时，可能是模型太大或硬件性能不足"
        
    except Exception as e:
        print(f"\n[!] 启动失败: {e}")
        return False, str(e)

@app.route('/', methods=['GET'])
def index():
    return {
        "status": "running",
        "service": "Llama-Swap Proxy",
        "version": "1.0.0",
        "endpoints": [
            "/v1/chat/completions",
            "/v1/models",
            "/health",
            "/chat"
        ]
    }

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/chat', methods=['GET'])
def chat_ui():
    return send_file('chat.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (JS, CSS, etc.)"""
    try:
        return send_from_directory('assets', filename)
    except FileNotFoundError:
        return {"error": "Asset not found"}, 404

@app.route('/v1/chat/completions', methods=['POST'])
def proxy_chat():
    # 1. 安全检查：API Key
    if not check_auth():
        return {"error": "Invalid or missing API Key"}, 401

    data = request.json
    requested_model = data.get('model')
    
    if not requested_model:
        return {"error": "Model parameter is required"}, 400

    config = load_config()
    
    # 2. 检查并切换模型
    success, msg = start_model(requested_model, config)
    if not success:
        return {"error": f"Failed to start model: {msg}"}, 500

    # 3. 转发请求给 llama-server
    target_url = f"http://127.0.0.1:{LLAMA_SERVER_PORT}/v1/chat/completions"
    
    try:
        resp = requests.post(target_url, json=data, stream=True)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(stream_with_context(resp.iter_content(chunk_size=1024)),
                        status=resp.status_code,
                        headers=headers)
    except Exception as e:
        return {"error": f"Proxy error: {str(e)}"}, 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    # 列表接口也需要鉴权，防止泄漏你有哪些模型
    if not check_auth():
        return {"error": "Invalid or missing API Key"}, 401
        
    config = load_config()
    models_list = []
    for key in config['models']:
        models_list.append({
            "id": key,
            "object": "model",
            "owned_by": "user"
        })
    return {"object": "list", "data": models_list}

def signal_handler(sig, frame):
    print("\n[!] 正在关闭...")
    stop_current_server()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    print(f"[*] 安全代理已启动")
    print(f"    地址: http://{BIND_HOST}:{PROXY_PORT}")
    # 隐藏 API Key 的显示
    masked_key = PROXY_API_KEY[:3] + "*" * 5 + PROXY_API_KEY[-3:] if PROXY_API_KEY and len(PROXY_API_KEY) > 6 else "******"
    print(f"    API Key: {masked_key}")
    print(f"    (请确保客户端使用此 Key，否则会被拒绝)")
    
    # host=BIND_HOST 强制绑定到 127.0.0.1，这是防火墙的第一道防线
    app.run(host=BIND_HOST, port=PROXY_PORT, debug=False, threaded=True)

# === 新增：启动后自动加载一个默认模型（可选）===
# === 新增：程序关闭时自动清理进程 ===
def signal_handler(sig, frame):
    print("\n[!] 正在关闭代理和模型进程...")
    stop_current_server()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)  # 再加一个，兼容性更好
    
    print(f"[*] Llama-Swap 安全代理已启动")
    print(f"    访问地址 → http://{BIND_HOST}:{PROXY_PORT}/chat")
    print(f"    模型列表 → http://{BIND_HOST}:{PROXY_PORT}/v1/models")
    masked_key = PROXY_API_KEY[:4] + "****" + PROXY_API_KEY[-4:] if len(PROXY_API_KEY) > 8 else "******"
    print(f"    当前 API Key → {masked_key}")
    print(f"    提示：请确保 chat.html 中 BASE_API_URL 改为空字符串 \"\"")
    print("="*60)

    # 可选：启动时自动加载一个默认模型（强烈推荐）
    try:
        config = load_config()
        default_model = config.get("default_model") or config.get("defaultModel")
        if default_model and default_model in config['models']:
            print(f"[+] 正在预加载默认模型：{default_model}")
            start_model(default_model, config)
        else:
            print(f"[+] 未设置 default_model，首次使用时会自动加载请求的模型")
    except Exception as e:
        print(f"[!] 预加载默认模型失败（可忽略）：{e}")

    app.run(host=BIND_HOST, port=PROXY_PORT, debug=False, threaded=True)