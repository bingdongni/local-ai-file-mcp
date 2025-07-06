import os
from src.file_loader import load_file


def test_load_txt():
    # 创建临时txt文件
    test_content = "This is a test file."
    with open("test.txt", "w") as f:
        f.write(test_content)

    result = load_file("test.txt")

    assert result['type'] == 'txt'
    assert result['status'] == 'success'
    assert result['content'] == test_content

    # 清理
    os.remove("test.txt")


def test_load_pdf():
    # 假设tests目录下有sample.pdf
    result = load_file("tests/sample.pdf")

    assert result['type'] == 'pdf'
    assert result['status'] == 'success'
    assert len(result['content']) > 0


def test_unsupported_file():
    result = load_file("test.docx")

    assert result['type'] == 'error'
    assert result['status'] == 'error'
    assert "Unsupported file type" in result['content']
