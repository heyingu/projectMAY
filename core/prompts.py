# -*- coding: utf-8 -*-
from langchain.prompts import PromptTemplate

def get_prompt_template():
    """问答提示词模板"""
    template = """用户问题：{question}

相关法律条文：{context}

请按照以下格式输出：
        1. 结论（合规/部分合规/不合规）
        2. 理由（列出条款编号和理由） 
"""
    return PromptTemplate(
        template=template,
        input_variables=["question", "context"]
    )