# LLM集成指南

## 1. 准备LLM模型

### 1.1 下载模型
你可以从以下来源下载兼容的LLM模型:
- Hugging Face: https://huggingface.co/models
- llama.cpp: https://github.com/ggerganov/llama.cpp

推荐使用量化后的模型，如7B或13B参数的GGUF/GGML格式。

### 1.2 放置模型
将下载的模型文件放在`models/`目录下

## 2. 配置环境变量
在项目根目录创建`.env`文件，配置LLM相关参数:
```env
MODEL_PATH=./models/llama-7b.ggmlv3.q4_0.bin
MODEL_N_CTX=2048
MODEL_TEMPERATURE=0.1
