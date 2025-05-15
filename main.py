# -*- coding: utf-8 -*-
from core.data_loader import load_special_document, create_documents_from_sections
from core.text_splitter import split_policy_documents
from core.parallel import process_files_concurrently
from core.llm import LLMClient
from config import config

def main():
    # 初始化系统
    llm_client = LLMClient()
    
    # 处理法律文档
    raw_text = load_special_document()
    sections = split_policy_documents(raw_text)
    docs = create_documents_from_sections(sections)
    
    # 处理问题文件
    all_questions = []
    for chunks in process_files_concurrently():
        all_questions.extend(chunks)
    
    # ...（后续向量库构建和问答逻辑）

if __name__ == "__main__":
    main()