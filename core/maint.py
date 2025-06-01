# core/maint.py
from core.data_loader import load_special_document, create_documents_from_sections, process_directory
from core.text_splitter import split_policy_documents
from core.embeddings import get_embeddings
from core.vectorstore import build_vectorstore
from core.llm import LLMClient
from core.prompts import get_prompt_template
from core.parallel import process_files_concurrently, process_queries_concurrently
from core.qa_chain import create_qa_chain
from config import config
import os
import dashscope


def process_directory_and_get_results(root_directory):
    """
    接收目录路径，处理文件并返回问答结果

    参数:
        root_directory (str): 用户上传文件的临时目录路径

    返回:
        List[Dict]: 包含问题和回答的字典列表
    """
    try:
        # 环境变量校验
        if not config.DASHSCOPE_API_KEY:
            raise ValueError("未找到 DASHSCOPE_API_KEY，请设置环境变量")

        # 构建向量数据库
        legal_docs = []
        vectorstore = build_vectorstore(legal_docs)

        # 初始化大语言模型
        llm_client = LLMClient()
        prompt = get_prompt_template()
        qa_chain = create_qa_chain(vectorstore=vectorstore, llm=llm_client.get_client(), prompt=prompt)
        # 处理指定目录（替换为用户上传路径）
        process_directory(root_directory)

        # 读取用户问题文件
        all_queries = []
        for chunks in process_files_concurrently():
            all_queries.extend(chunks)

        # 并行处理问答
        results = process_queries_concurrently(qa_chain, all_queries)
        return results

    except Exception as e:
        raise RuntimeError(f"处理失败: {str(e)}")