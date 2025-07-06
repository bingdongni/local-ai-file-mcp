import os
from src.document_processor import DocumentProcessor


def test_process_file():
    # 创建临时文件
    with open("test.txt", "w") as f:
        f.write("这是一个测试文件，用于测试文档处理。")

    processor = DocumentProcessor()
    result = processor.process_file("test.txt")

    assert result['status'] == 'success'
    assert 'doc_id' in result
    assert result['document']['type'] == 'txt'
    assert "测试文件" in result['document']['content']

    # 清理
    os.remove("test.txt")


def test_process_directory(tmpdir):
    # 创建临时目录和文件
    test_dir = tmpdir.mkdir("test_dir")

    # 创建txt文件
    txt_file = test_dir.join("test1.txt")
    txt_file.write("这是第一个测试文件。")

    # 创建pdf文件（使用空文件模拟）
    pdf_file = test_dir.join("test2.pdf")
    pdf_file.write("")

    processor = DocumentProcessor()
    results = processor.process_directory(str(test_dir))

    assert len(results) == 2
    assert all(r['status'] == 'success' for r in results)

    # 验证文档数量
    count = processor.get_document_count()
    assert count >= 2
