# -*- coding: utf-8 -*-
import dashscope
from langchain_community.llms import Tongyi
from config import config
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    def __init__(self, timeout=None):
        """
        初始化大模型客户端
        :param timeout: 可覆盖config的默认超时设置（秒）
        """
        self.timeout = timeout or config.TIMEOUT_CONFIG['llm_timeout']

        # 带重试机制的客户端
        self.llm = self._create_llm_with_retry()

    def _create_llm_with_retry(self):
        """创建带重试机制的LLM实例"""
        return Tongyi(
            model_name=config.LLM_MODEL,
            dashscope_api_key=config.DASHSCOPE_API_KEY,
            timeout=self.timeout,
            streaming_timeout=config.TIMEOUT_CONFIG['stream_timeout'],
            top_p=0.8,
            temperature=0.1
        )

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10))
    def safe_call(self, prompt, timeout=None):
        """安全调用方法（自动重试）"""
        current_timeout = timeout or self.timeout
        return self.llm.generate(
            [prompt],
            timeout=current_timeout
        )

    def get_client(self):
        """获取原始客户端（兼容旧代码）"""
        return self.llm

    @property
    def model_config(self):
        """获取当前模型配置"""
        return {
            'model': config.LLM_MODEL,
            'timeout': self.timeout,
            'max_retries': 3
        }