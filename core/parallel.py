# -*- coding: utf-8 -*-
import glob
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import config

def process_files_concurrently(root_dir="D:\\ProcessedFiles"):
    # 收集符合条件的文件路径（只处理 _cl.txt 文件，排除 laws.txt）
    file_paths = [
        f for f in glob.glob(os.path.join(root_dir, "*"))
        if os.path.isfile(f) and
        os.path.basename(f) != "laws.txt" and
        os.path.basename(f).endswith("_cl.txt")
    ]

    # 使用 map 并发执行，并保证返回结果顺序与输入顺序一致
    with ThreadPoolExecutor(max_workers=config.WORKER_NUM) as executor:
        results = list(executor.map(process_single_file, file_paths))

    return results

def process_single_file(file_path):
    from core.data_loader import general_file_loader

    print(f"Processing: {file_path}")
    try:
        data = general_file_loader(file_path)

        full_text = "\n".join([d.page_content for d in data])

        lines = [line.strip() for line in full_text.split('\n') if line.strip()]

        print(f"Total lines: {len(lines)}")
        print("First 10 lines:")
        for line in lines[:10]:
            print(line)

        chunks = ['\n'.join(lines[i:i + 5]) for i in range(0, len(lines), 5)]

        print("Chunk order (first and last):")
        print("First chunk:", chunks[0])
        print("Last chunk :", chunks[-1] if chunks else "None")

        return chunks
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def process_queries_concurrently(qa_chain, queries, max_workers=None):
    from config import config
    max_workers = max_workers or config.WORKER_NUM

    def query_function(query):
        """封装qa_chain.run逻辑，便于使用executor.map"""
        return {"question": query, "result": qa_chain.run(query)}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用map方法，保证结果顺序与queries顺序一致
        results = list(executor.map(query_function, queries))

    return results