# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # 强制加载 .env 文件


class Config:
    # 模型配置
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "qwen-max"

    # 文本处理配置
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_POLICIES = 32

    # 并行处理
    WORKER_NUM = 4

    # 路径配置
    LAW_FILE = "laws.txt"

    # API 密钥（全大写属性名）
    @property
    def DASHSCOPE_API_KEY(self):
        key = os.getenv("DASHSCOPE_API_KEY")
        if not key or not key.startswith("sk-"):
            raise ValueError("未找到有效的 API KEY")
        return key


config = Config()