# -*- coding: utf-8 -*-
from langchain.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain.docstore.document import Document
from .text_splitter import split_policy_documents
import os
import requests
import tempfile
OLMOCR_API_URL = "http://127.0.0.1:8000/ocr"
def load_special_document(file_path="laws.txt"):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    raw_text = documents[0].page_content if documents else ""
    return raw_text

def call_olmocr(pdf_path):
    """
    调用本地或远程的 olmOCR API 来解析 PDF 文件。
    返回提取后的纯文本内容。
    """
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        response = requests.post(OLMOCR_API_URL, files=files)

    if response.status_code == 200:
        result = response.json()
        # 假设返回结果中有一个 'text' 字段包含提取出的文本
        return result.get("text", "")
    else:
        raise Exception(f"olmOCR API 调用失败: {response.status_code}, {response.text}")


def process_pdf_with_olmocr(file_path):
    """
    使用 olmOCR 提取 PDF 内容并保存为临时 txt 文件。
    """
    temp_txt_path = os.path.splitext(file_path)[0] + "_olmocr.txt"

    extracted_text = call_olmocr(file_path)

    with open(temp_txt_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return temp_txt_path


def general_file_loader(file_path):
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    # elif file_path.endswith(".docx"):
    #     loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".pdf"):
        # 使用 olmOCR 解析 PDF
        temp_txt_path = process_pdf_with_olmocr(file_path)
        # 使用 TextLoader 加载生成的文本文件
        loader = TextLoader(temp_txt_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    return loader.load()

def create_documents_from_sections(sections):
    return [Document(page_content=section) for section in sections]