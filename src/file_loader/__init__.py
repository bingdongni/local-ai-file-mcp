from typing import Dict, Any
from .txt_loader import load_txt
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .excel_loader import load_excel

def load_file(file_path: str) -> Dict[str, Any]:
    if file_path.endswith('.txt'):
        return load_txt(file_path)
    elif file_path.endswith('.pdf'):
        return load_pdf(file_path)
    elif file_path.endswith('.docx'):
        return load_docx(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return load_excel(file_path)
    elif file_path.endswith('.pptx'):
        return load_ppt(file_path)
    else:
        return {
            'content': f"Unsupported file type: {file_path}",
            'type': 'error',
            'size': 0,
            'status': 'error',
            'metadata': {}
        }