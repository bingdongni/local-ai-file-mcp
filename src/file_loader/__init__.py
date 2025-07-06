from typing import Dict, Any
from .txt_loader import load_txt
from .pdf_loader import load_pdf

def load_file(file_path: str) -> Dict[str, Any]:
    if file_path.endswith('.txt'):
        content = load_txt(file_path)
        return {
            'content': content,
            'type': 'txt',
            'size': len(content),
            'status': 'success' if content else 'error'
        }
    elif file_path.endswith('.pdf'):
        content = load_pdf(file_path)
        return {
            'content': content,
            'type': 'pdf',
            'size': len(content),
            'status': 'success' if content else 'error'
        }
    else:
        return {
            'content': f"Unsupported file type: {file_path}",
            'type': 'error',
            'size': 0,
            'status': 'error'
        }
