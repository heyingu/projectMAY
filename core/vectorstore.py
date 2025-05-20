# -*- coding: utf-8 -*-
from langchain.vectorstores import FAISS
from .embeddings import get_embeddings
from pymongo import MongoClient
from pymongo import errors
import hashlib
from pymongo.errors import BulkWriteError
from langchain.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
import os
import numpy as np
os.environ["DASHSCOPE_API_KEY"] = 'sk-12cee5f31a6d4c0b9c000019cdeba574'
def build_vectorstore(docs):
    """构建向量数据库"""
    embedding_model = DashScopeEmbeddings(
        model="text-embedding-v2",
    )
    texts = [doc.page_content for doc in docs]  # 文本内容列表（字符串）
    embeddings_1= embedding_model.embed_documents(texts)  # 嵌入向量列表
    metadata = [doc.metadata for doc in docs]  # 元数据列表（字典）

    # 连接到 MongoDB
    connection_string_read = "mongodb://readonly_user:wyx123@10.234.176.114:27017/?authSource=公平竞争规则"#只读
    connection_string_admin = "mongodb://admin:wyx15757569582@localhost:27017/?authSource=admin"  # 管理
    client = MongoClient(connection_string_read)
    db = client['公平竞争规则']
    collection = db['list1']

    #管理的时候is_adimin是1，可以插入数据，只读的时候就直接跳过插入数据，记得改clinet里的内容
    #错误: E11000 duplicate key error collection这个错误表示有内容重复了
    is_admin = 0
    if is_admin:
        # 构建带哈希ID的文档
        documents = [
            {
                "_id": hashlib.md5(f"{text}{meta.get('source', '')}".encode()).hexdigest(),
                "file_info": meta,
                "embedding": embedding,
                "text_content": text,
                "dimension": len(embedding)  # 记录向量维度
            }
            for meta, embedding, text in zip(metadata, embeddings_1, texts)
        ]

        # 分批插入（每批1000条）
        batch_size = 1000
        total_success = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                result = collection.insert_many(batch, ordered=False)
                total_success += len(result.inserted_ids)
                print(f"批次 {i // batch_size + 1} 插入成功: {len(result.inserted_ids)} 条")
            except errors.BulkWriteError as e:
                # 获取所有写错误
                write_errors = e.details['writeErrors']

                for error in write_errors:
                    index = error['index']  # 出错的文档在 batch 中的位置
                    failed_document = batch[index]  # 获取失败的文档
                    errmsg = error['errmsg']  # 错误信息

                    # 提取并打印 'text_content' 字段的内容
                    text_content = failed_document.get('text_content', '无')

                    # 打印或记录失败的文档和错误信息
                    print(
                        f"批次 {i // batch_size + 1} 第 {index + 1} 条文档插入失败（_id: {failed_document.get('_id')}），错误: {errmsg}")
                    print(f"失败文档的文本内容: {text_content}")

                total_success += (batch_size - len(write_errors))
                print(f"批次 {i // batch_size + 1} 部分失败: {len(write_errors)} 条")
    else:
        print(f"只读权限进入数据库")

    # 1. 从MongoDB加载数据
    data = list(collection.find({}))
    texts_mongodb = [doc["text_content"] for doc in data]
    embeddings_mongodb= np.array([doc["embedding"] for doc in data])  # 转为numpy数组
    metadatas_mongodb = [doc["file_info"] for doc in data]

    return  FAISS.from_embeddings(
    text_embeddings=list(zip(texts_mongodb, embeddings_mongodb)),
    embedding=embedding_model,
    metadatas=metadatas_mongodb
)