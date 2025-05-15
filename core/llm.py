# -*- coding: utf-8 -*-
from langchain_community.llms import Tongyi
from config import config

class LLMClient:
    def __init__(self):
        self.llm = Tongyi(
            model_name=config.LLM_MODEL,
            dashscope_api_key=config.DASHSCOPE_API_KEY
        )
    
    def get_client(self):
        return self.llm