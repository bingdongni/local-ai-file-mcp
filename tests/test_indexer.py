import os
from src.indexer.chroma_index import (
    get_chroma_client,
    get_or_create_collection,
    reset_index,
    add_document,
    add_documents,
    count_documents,
    search,
    search_by_id
)


def test_index_and_search():
    # 初始化客户端和集合
    client = get_chroma_client()
    collection = reset_index(client)

    # 添加测试文档
    doc1 = {
        'content': '这是一个关于人工智能的测试文档。',
        'type': 'txt',
        'metadata': {'category': '技术'}
    }

    doc2 = {
        'content': '这是一个关于机器学习的示例文档。',
        'type': 'pdf',
        'metadata': {'category': '技术'}
    }

    doc3 = {
        'content': '这是一个关于市场营销的文档。',
        'type': 'docx',
        'metadata': {'category': '商业'}
    }

    # 添加文档
    doc1_id = add_document(collection, doc1)
    doc2_id = add_document(collection, doc2)
    add_document(collection, doc3)

    # 验证文档数量
    assert count_documents(collection) == 3

    # 按ID检索
    retrieved = search_by_id(collection, doc1_id)
    assert retrieved is not None
    assert "人工智能" in retrieved['document']

    # 执行搜索
    results = search(collection, "机器学习", n_results=2)
    assert len(results) >= 1
    assert "机器学习" in results[0]['document']
    assert results[0]['score'] > 0.8

    # 带过滤的搜索
    results = search(collection, "文档", filter={"category": "商业"})
    assert len(results) >= 1
    assert "市场营销" in results[0]['document']
