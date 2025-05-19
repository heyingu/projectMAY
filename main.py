# -*- coding: utf-8 -*-
#pip install langchain langchain-community faiss-cpu python-docx pypdf dashscope sentence-transformers
from core.data_loader import load_special_document, create_documents_from_sections
from core.text_splitter import split_policy_documents
from core.embeddings import get_embeddings
from core.vectorstore import build_vectorstore
from core.llm import LLMClient
from core.prompts import get_prompt_template
from core.parallel import process_files_concurrently, process_queries_concurrently
from core.qa_chain import create_qa_chain
from config import config
import os

def main():
    try:
        # ================== 环境变量准备阶段 ==================
        # 环境变量校验
        if not config.DASHSCOPE_API_KEY:
            raise ValueError("未找到 DASHSCOPE_API_KEY，请设置环境变量")

        # ================== 数据处理阶段 ==================
        # 加载并处理法律文档
        print("\n[阶段1] 正在加载核心法律文档...")
        raw_text = load_special_document("laws.txt")
        policy_sections = split_policy_documents(raw_text)
        legal_docs = create_documents_from_sections(policy_sections)
        print(f"→ 成功加载 {len(legal_docs)} 条法律条款")

        # 初始化 Embedding 模型
        print("\n[阶段2] 正在初始化语义嵌入模型...")
        embeddings = get_embeddings()

        # 构建向量数据库
        print("\n[阶段3] 正在构建法律知识向量库...")
        vectorstore = build_vectorstore(legal_docs)
        print(f"→ 向量库已包含 {vectorstore.index.ntotal} 个向量")

        # ================== 模型准备阶段 ==================
        # 初始化大语言模型
        print("\n[阶段4] 正在初始化通义千问大模型...")
        llm_client = LLMClient()
        
        # 准备 Prompt 模板
        print("\n[阶段5] 正在加载提示词模板...")
        prompt = get_prompt_template()

        # 构建 QA 链
        print("\n[阶段6] 正在构建智能问答链...")
        qa_chain = create_qa_chain(
            vectorstore=vectorstore,
            llm=llm_client.get_client(),
            prompt=prompt
        )

        # ================== 问答处理阶段 ==================
        # 读取用户问题文件
        print("\n" + "="*30 + " 开始处理用户问题 " + "="*30)
        print("\n[阶段7] 正在扫描并解析用户问题文件...")
        all_queries = []
        for chunks in process_files_concurrently():
            all_queries.extend(chunks)
        print(f"→ 共发现 {len(all_queries)} 条待处理问题")

        # 并行处理问答
        print("\n[阶段8] 启动并行推理引擎...")
        results = process_queries_concurrently(qa_chain, all_queries)

        # ================== 结果输出阶段 ==================
        print("\n" + "="*30 + " 最终推理结果 " + "="*30)
        for idx, item in enumerate(results, 1):
            print(f"\n🔍 问题 {idx}/{len(results)}")
            print(f"❓ {item['question']}")
            print(f"📝 回答：\n{item['result']}")
            print("-" * 60)

    except Exception as e:
        print(f"\n❌ 系统运行异常: {str(e)}")
        if isinstance(e, KeyboardInterrupt):
            print("用户中断操作")
    finally:
        print("\n✅ 系统运行完成")

if __name__ == "__main__":
    # 设置终端编码支持中文
    import sys
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout.reconfigure(encoding='utf-8')
    main()