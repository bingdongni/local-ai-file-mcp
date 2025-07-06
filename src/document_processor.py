import os
import logging
from typing import List, Dict, Any
from src.file_loader import load_file
from src.indexer.chroma_index import (
    get_chroma_client,
    get_or_create_collection,
    add_document,
    add_documents,
    count_documents
)


class DocumentProcessor:
    def __init__(self):
        self.client = get_chroma_client()
        self.collection = get_or_create_collection(self.client)

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件并添加到索引"""
        try:
            logging.info(f"Processing file: {file_path}")

            # 加载文件内容
            document = load_file(file_path)

            # 添加元数据
            document['metadata']['file_path'] = file_path
            document['metadata']['file_size'] = os.path.getsize(file_path)

            # 添加到索引
            doc_id = add_document(self.collection, document)

            result = {
                'status': 'success',
                'doc_id': doc_id,
                'document': document
            }

            return result

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'file_path': file_path
            }

    def process_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """处理目录下的所有文件并添加到索引"""
        if extensions is None:
            extensions = ['.txt', '.pdf', '.docx', '.xlsx', '.xls', '.pptx']

        results = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    result = self.process_file(file_path)
                    results.append(result)

        return results

    def get_document_count(self) -> int:
        """获取索引中的文档数量"""
        return count_documents(self.collection)
