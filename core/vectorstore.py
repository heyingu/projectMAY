# -*- coding: utf-8 -*-
from langchain.vectorstores import FAISS
from .embeddings import get_embeddings
from pymongo import MongoClient
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
    client = MongoClient('mongodb://localhost:27017/')
    db = client['公平竞争规则']
    collection = db['list1']

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
        except BulkWriteError as e:
            total_success += (batch_size - len(e.details['writeErrors']))
            print(f"批次 {i // batch_size + 1} 部分失败: {len(e.details['writeErrors'])} 条")

    print(f"✅ 全部完成！共成功插入 {total_success}/{len(documents)} 条记录")

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