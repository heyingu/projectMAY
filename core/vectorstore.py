# -*- coding: utf-8 -*-
from langchain.vectorstores import FAISS
from .embeddings import get_embeddings

def build_vectorstore(docs):
    """构建向量数据库"""
    return FAISS.from_documents(
        documents=docs,
        embedding=get_embeddings()
    )