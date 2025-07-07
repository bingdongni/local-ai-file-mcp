import os
import sys
import uvicorn

# 将项目根目录添加到 Python 路径（关键修复）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_server.main import app
from src.config import SERVER_HOST, SERVER_PORT, SERVER_LOG_LEVEL

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=SERVER_LOG_LEVEL,
        timeout_keep_alive=60
    )