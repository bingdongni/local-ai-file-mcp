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


def test_load_docx():
    # 创建临时docx文件
    from docx import Document

    doc = Document()
    doc.add_heading('Test Document', 0)
    doc.add_paragraph('This is a test paragraph.')

    table = doc.add_table(rows=2, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Name'
    hdr_cells[1].text = 'Age'
    row_cells = table.rows[1].cells
    row_cells[0].text = 'John'
    row_cells[1].text = '30'

    doc.save('test.docx')

    result = load_file('test.docx')

    assert result['type'] == 'docx'
    assert result['status'] == 'success'
    assert 'Test Document' in result['content']
    assert 'John' in result['content']
    assert '30' in result['content']

    # 验证元数据
    assert 'author' in result['metadata']
    assert 'created' in result['metadata']

    # 清理
    os.remove('test.docx')
