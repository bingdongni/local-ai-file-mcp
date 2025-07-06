import pytest
from fastapi.testclient import TestClient
from src.mcp_server.main import app, processor
from src.indexer.chroma_index import reset_index

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test():
    # 重置索引
    reset_index(processor.collection)
    yield
    # 清理
    reset_index(processor.collection)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_file(tmpdir):
    # 创建临时文件
    test_file = tmpdir.join("test.txt")
    test_file.write("这是一个测试文件，用于API测试。")

    with open(str(test_file), "rb") as f:
        response = client.post("/upload", files={"file": f})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "doc_id" in response.json()


def test_search():
    # 先上传测试文档
    test_data = {
        "content": "这是一个关于Python编程的测试文档。",
        "type": "txt",
        "metadata": {"category": "技术"}
    }
    processor.collection.add(
        ids=["test1"],
        documents=[test_data["content"]],
        metadatas=[test_data["metadata"]]
    )

    # 执行搜索
    response = client.post("/search", json={"query": "Python"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert "Python" in results[0]["content"]


def test_mcp_search():
    # 先上传测试文档
    test_data = {
        "content": "这是一个关于机器学习的测试文档。",
        "type": "pdf",
        "metadata": {"category": "AI"}
    }
    processor.collection.add(
        ids=["test2"],
        documents=[test_data["content"]],
        metadatas=[test_data["metadata"]]
    )

    # 执行MCP搜索
    response = client.post("/mcp/file_search", json={"query": "机器学习"})

    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "file_search"
    assert "parameters" in response.json()
    assert "results" in response.json()["parameters"]
    assert len(response.json()["parameters"]["results"]) >= 1
