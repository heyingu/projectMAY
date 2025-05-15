# -*- coding: utf-8 -*-
import os

class Config:
    # 模型配置
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "qwen-max"
    
    # 文件处理配置
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_POLICIES = 32
    WORKER_NUM = 4
    
    # API 密钥（从环境变量获取）
    @property
    def DASHSCOPE_API_KEY(self):
        #export DASHSCOPE_API_KEY="sk-7fb2aee47f5d4531855a7ac3412249fe"
        return os.getenv("DASHSCOPE_API_KEY", "sk-default-key")


config = Config()