# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # 强制加载 .env 文件


class Config:
    # 模型配置
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "qwen-max"

    # ===== 超时控制配置 =====
    TIMEOUT_CONFIG = {
        'http_timeout': 30,  # 底层HTTP请求超时（秒）
        'llm_timeout': 120,  # 模型推理超时
        'stream_timeout': 60,  # 流式响应超时
        'retry_timeout': 240,  # 含重试的总超时
        'chain_timeout': 240  # 问答链整体超时
    }

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
        if not key:
            raise ValueError("未检测到DASHSCOPE_API_KEY环境变量！")
        return key

    # ===== 动态超时计算 =====
    @staticmethod
    def dynamic_timeout(text_length):
        """根据文本长度自动计算超时时间"""
        base = 30
        extra = min(text_length // 500 * 5, 300)  # 每500字符增加5秒，上限300秒
        return base + extra


config = Config()