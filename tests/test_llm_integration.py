import pytest
from src.llm_integration import LLMIntegration
from src.indexer.chroma_index import get_chroma_client, reset_index


@pytest.mark.skip(reason="需要本地LLM模型才能运行")
def test_llm_integration():
    # 重置索引
    client = get_chroma_client()
    reset_index(client)

    # 添加测试文档
    collection = client.get_or_create_collection("documents")
    collection.add(
        ids=["test1"],
        documents=["Python是一种广泛使用的高级编程语言。"],
        metadatas=[{"type": "txt", "category": "编程"}]
    )

    # 初始化LLM集成
    llm_integration = LLMIntegration(client)

    # 提问
    question = "Python是什么?"
    result = llm_integration.ask(question)

    # 验证结果
    assert "answer" in result
    assert "source_documents" in result
    assert len(result["source_documents"]) >= 1
    assert "Python" in result["source_documents"][0]["content"]
