python
运行
from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.document_processor import DocumentProcessor
from src.indexer.chroma_index import search

# 初始化FastAPI应用
app = FastAPI(
    title="MCP文件检索服务",
    description="基于MCP协议的文件检索与问答服务",
    version="0.1.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化文档处理器
processor = DocumentProcessor()


# 请求模型定义
class SearchRequest(BaseModel):
    query: str
    limit: int = 3
    file_types: Optional[List[str]] = None


class FileSearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class SearchResponse(BaseModel):
    results: List[FileSearchResult]
    total: int


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "details": str(exc)}
    )


# 健康检查接口
@app.get("/health")
def health_check():
    """检查服务健康状态"""
    return {
        "status": "ok",
        "document_count": processor.get_document_count(),
        "timestamp": str(os.path.getctime(__file__))
    }


# 单文件上传接口
@app.post("/upload")
async def upload_file(
        file: UploadFile = File(..., max_size=100_000_000)  # 限制100MB
):
    """上传单个文件并添加到索引"""
    try:
        # 保存临时文件
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 检查文件类型
        allowed_extensions = ['.txt', '.pdf', '.docx', '.xlsx', '.xls', '.pptx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}，支持的类型: {', '.join(allowed_extensions)}"
            )

        # 处理文件
        result = processor.process_file(temp_path)

        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return result

    except HTTPException as e:
        # 清理可能残留的临时文件
        temp_path = f"temp_{file.filename}"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
    except Exception as e:
        # 清理可能残留的临时文件
        temp_path = f"temp_{file.filename}"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        logging.error(f"上传文件失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


# 批量文件上传接口
@app.post("/upload/batch")
async def upload_files(
        files: List[UploadFile] = File(..., max_size=500_000_000)  # 总限制500MB
):
    """批量上传文件并添加到索引"""
    results = []
    for file in files:
        try:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())

            # 检查文件类型
            allowed_extensions = ['.txt', '.pdf', '.docx', '.xlsx', '.xls', '.pptx']
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                results.append({
                    'status': 'error',
                    'filename': file.filename,
                    'error': f"不支持的文件类型: {file_ext}"
                })
                continue

            result = processor.process_file(temp_path)
            results.append(result)

            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            results.append({
                'status': 'error',
                'filename': file.filename,
                'error': str(e)
            })
        finally:
            # 确保临时文件被删除
            temp_path = f"temp_{file.filename}"
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return {
        "total_files": len(files),
        "success_count": sum(1 for r in results if r.get('status') == 'success'),
        "results": results
    }


# 搜索接口
@app.post("/search", response_model=SearchResponse)
def file_search(request: SearchRequest):
    """根据查询词搜索相关文档"""
    try:
        # 构建过滤条件
        filter = {}
        if request.file_types:
            filter["type"] = {"$in": request.file_types}

        # 执行搜索
        results = search(processor.collection, request.query, request.limit, filter)

        return {
            "results": results,
            "total": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MCP协议兼容接口
@app.post("/mcp/file_search")
def mcp_file_search(request: SearchRequest):
    """MCP协议兼容的文件搜索接口"""
    try:
        # 执行搜索
        results = search(processor.collection, request.query, request.limit)

        # 转换为MCP格式
        mcp_response = {
            "name": "file_search",
            "parameters": {
                "query": request.query,
                "results": [
                    {
                        "content": hit["document"],
                        "metadata": hit["metadata"],
                        "score": hit["score"]
                    }
                    for hit in results
                ]
            }
        }

        return mcp_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 检索与问答接口
@app.post("/retrieve_answer")
def retrieve_answer(request: SearchRequest):
    """根据查询检索文档并生成回答"""
    try:
        # 执行搜索获取相关文档
        results = search(processor.collection, request.query, request.limit)

        if not results:
            return {
                "answer": "抱歉，没有找到与查询相关的文档。",
                "source_documents": []
            }

        # 构建提示模板
        prompt = (
            f"用户问题: {request.query}\n\n"
            f"参考以下文档内容回答问题:\n\n"
        )

        # 添加检索结果到提示
        source_documents = []
        for i, hit in enumerate(results):
            prompt += f"文档 {i + 1}:\n{hit['document']}\n\n"
            source_documents.append({
                "content": hit["document"],
                "metadata": hit["metadata"],
                "score": hit["score"]
            })

        # 这里应该调用LLM模型，暂时返回提示
        answer = "基于检索到的文档，答案如下:\n\n"
        answer += "由于未连接实际的LLM模型，此处为示例回答。\n"
        answer += "在实际部署中，这里会调用本地LLM生成回答。"

        return {
            "answer": answer,
            "source_documents": source_documents,
            "prompt_used": prompt  # 调试用，可在生产环境移除
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
