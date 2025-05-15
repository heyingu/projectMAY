# -*- coding: utf-8 -*-
# core/embeddings.py
from langchain.embeddings import HuggingFaceEmbeddings
from config import config

class EmbeddingManager:
    """Embedding 模型管理器"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化 Embedding 模型"""
        self.model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},  # 可改为 "cuda" 使用 GPU
            encode_kwargs={"normalize_embeddings": False}
        )

    def get_embeddings(self):
        """获取 Embedding 模型实例"""
        return self.model

def get_embeddings():
    """快捷获取 Embedding 的工厂函数"""
    return EmbeddingManager().get_embeddings()