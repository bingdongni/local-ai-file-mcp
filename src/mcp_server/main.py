from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from src.document_processor import DocumentProcessor
from src.indexer.chroma_index import search

app = FastAPI(
    title="MCP文件检索服务",
    description="基于MCP协议的文件检索与问答服务",
    version="0.1.0"
)

# 初始化文档处理器
processor = DocumentProcessor()


# 请求模型
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


# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok", "document_count": processor.get_document_count()}


# 文件上传接口
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 保存临时文件
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 处理文件
        result = processor.process_file(temp_path)

        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 批量上传接口
@app.post("/upload/batch")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())

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

    return results


@app.post("/search", response_model=SearchResponse)
def file_search(request: SearchRequest):
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


# 修正缩进后的检索与问答接口
@app.post("/retrieve_answer")
def retrieve_answer(request: SearchRequest):
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
        answer += "由于未连接实际的LLM模型，此处为示例回答。"
        answer += "在实际部署中，这里会调用本地LLM生成回答。"

        return {
            "answer": answer,
            "source_documents": source_documents
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))