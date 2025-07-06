import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

# 索引目录
INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../index")
os.makedirs(INDEX_DIR, exist_ok=True)


def get_chroma_client():
    """获取ChromaDB客户端，支持持久化存储"""
    return chromadb.PersistentClient(path=INDEX_DIR)


def get_or_create_collection(client):
    """获取或创建文档集合"""
    # 使用Sentence Transformer作为嵌入函数
    embed_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 创建或获取集合
    return client.get_or_create_collection(
        name="documents",
        embedding_function=embed_function,
        metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
    )


def reset_index(client):
    """重置索引（用于测试）"""
    client.delete_collection(name="documents")
    return get_or_create_collection(client)


def add_document(collection, document: Dict[str, Any], external_id: str = None):
    """添加单个文档到索引"""
    doc_id = external_id or str(hash(document['content']))

    # 提取元数据
    metadata = {
        'type': document.get('type', 'unknown'),
        'size': document.get('size', 0),
        'status': document.get('status', 'unknown')
    }

    # 合并文档自带的元数据
    if 'metadata' in document:
        metadata.update(document['metadata'])

    # 添加到集合
    collection.add(
        ids=[doc_id],
        documents=[document['content']],
        metadatas=[metadata]
    )

    return doc_id


def add_documents(collection, documents: List[Dict[str, Any]]):
    """批量添加文档到索引"""
    doc_ids = []

    for doc in documents:
        doc_id = add_document(collection, doc)
        doc_ids.append(doc_id)

    return doc_ids


def count_documents(collection):
    """获取索引中文档数量"""
    return collection.count()


def search(collection, query: str, n_results: int = 3, filter: Dict = None):
    """执行语义搜索"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filter,
        include=["documents", "metadatas", "distances"]
    )

    # 处理搜索结果
    hits = []
    if results and 'documents' in results and results['documents']:
        for i in range(len(results['documents'][0])):
            hits.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'score': max(0, 1 - results['distances'][0][i])  # 将距离转换为相似度分数
            })

    return hits


def search_by_id(collection, doc_id: str):
    """根据ID检索文档"""
    results = collection.get(
        ids=[doc_id],
        include=["documents", "metadatas"]
    )

    if results and 'documents' in results and results['documents']:
        return {
            'document': results['documents'][0],
            'metadata': results['metadatas'][0]
        }
    return None