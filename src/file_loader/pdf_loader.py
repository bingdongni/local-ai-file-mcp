import logging
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_pdf(file_path: str) -> str:
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 合并所有页面内容
        full_text = "\n".join([doc.page_content for doc in documents])

        # 处理超大PDF（可选）
        if len(full_text) > 1000000:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000000,
                chunk_overlap=50000
            )
            texts = text_splitter.split_text(full_text)
            return texts[0]  # 只取第一部分
        else:
            return full_text

    except Exception as e:
        logging.error(f"Error loading PDF {file_path}: {str(e)}")
        return ""
