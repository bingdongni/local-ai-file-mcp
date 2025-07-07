import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# LLM配置
LLM_MODEL_PATH = os.environ.get("MODEL_PATH", "./models/llama-7b.ggmlv3.q4_0.bin")
LLM_N_CTX = int(os.environ.get("MODEL_N_CTX", 2048))
LLM_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", 0.1))

# 服务器配置
SERVER_HOST = os.environ.get("HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("PORT", 8000))
SERVER_LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

# 索引配置
INDEX_DIR = os.environ.get("INDEX_DIR", "./index")
