# -*- coding: utf-8 -*-
import dashscope
from langchain_community.llms import Tongyi
from config import config


class LLMClient:
    def __init__(self):
        try:
            # 显式设置 API Key（双重保障）
            dashscope.api_key = config.DASHSCOPE_API_KEY

            self.llm = Tongyi(
                model_name=config.LLM_MODEL,
                dashscope_api_key=config.DASHSCOPE_API_KEY  # ✅ 使用统一大写属性名
            )
        except Exception as e:
            print(f"❌ 模型初始化失败: {str(e)}")
            raise

    def get_client(self):
        return self.llm