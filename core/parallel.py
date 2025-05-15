# -*- coding: utf-8 -*-
import glob
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import config

def process_files_concurrently(root_dir="."):
    file_paths = [
        f for f in glob.glob(os.path.join(root_dir, "*")) 
        if os.path.isfile(f) and not os.path.basename(f) == "laws.txt"
    ]

    with ThreadPoolExecutor(max_workers=config.WORKER_NUM) as executor:
        futures = {executor.submit(process_single_file, f): f for f in file_paths}
        return [future.result() for future in as_completed(futures)]

def process_single_file(file_path):
    from core.data_loader import general_file_loader
    from core.text_splitter import RecursiveTextSplitter
    
    print(f"Processing: {file_path}")
    try:
        data = general_file_loader(file_path)
        full_text = "\n\n".join([d.page_content for d in data])
        return RecursiveTextSplitter().split_text(full_text)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def process_queries_concurrently(qa_chain, queries, max_workers=None):
    from config import config
    max_workers = max_workers or config.WORKER_NUM
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                lambda q: {"question": q, "result": qa_chain.run(q)},
                query
            ) for query in queries
        ]
        return [future.result() for future in as_completed(futures)]