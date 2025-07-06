import logging

def load_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        logging.error(f"Failed to decode {file_path} as UTF-8")
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        return ""
