import os
import logging
from typing import List, Dict, Any
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader

# 模型配置
MODEL_PATH = os.environ.get("MODEL_PATH", "./models/llama-7b.ggmlv3.q4_0.bin")
MODEL_N_CTX = int(os.environ.get("MODEL_N_CTX", 2048))
MODEL_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", 0.1))


class LLMIntegration:
    def __init__(self, chroma_client):
        self.chroma_client = chroma_client
        self.llm = self._init_llm()
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    def _init_llm(self):
        """初始化LLM模型"""
        try:
            logging.info(f"Loading LLM model from {MODEL_PATH}")
            llm = LlamaCpp(
                model_path=MODEL_PATH,
                n_ctx=MODEL_N_CTX,
                temperature=MODEL_TEMPERATURE,
                verbose=False
            )
            return llm
        except Exception as e:
            logging.error(f"Failed to load LLM model: {str(e)}")
            raise RuntimeError("LLM模型加载失败，请检查模型路径和配置")

    def get_qa_chain(self):
        """获取问答链"""
        # 创建向量存储
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name="documents",
            embedding_function=self.embeddings
        )

        # 创建检索器
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # 创建问答链
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

        return qa_chain

    def ask(self, question: str) -> Dict[str, Any]:
        """向LLM提问并获取回答"""
        try:
            qa_chain = self.get_qa_chain()
            result = qa_chain({"query": question})

            return {
                "answer": result["result"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result["source_documents"]
                ]
            }
        except Exception as e:
            logging.error(f"Error answering question: {str(e)}")
            return {
                "answer": f"抱歉，回答问题时出错: {str(e)}",
                "source_documents": []
            }
