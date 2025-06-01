# -*- coding: utf-8 -*-
from langchain.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain.docstore.document import Document
from .text_splitter import split_policy_documents
import os
import requests
import tempfile
import dashscope
from dashscope import Generation
OLMOCR_API_URL = "http://127.0.0.1:8000/ocr"
# 设置 DashScope API Key
dashscope.api_key = "sk-7fb2aee47f5d4531855a7ac3412249fe"  # 替换为你自己的 API Key
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
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".pdf"):
        # 使用 olmOCR 解析 PDF
        temp_txt_path = process_pdf_with_olmocr(file_path)
        # 使用 TextLoader 加载生成的文本文件
        loader = TextLoader(temp_txt_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    return loader.load()
def extract_policy_clauses_with_qwen(text):
    """
    使用 DashScope 上的 Qwen 模型提取政策条款
    :param text: 原始文本
    :return: 政策条款列表
    """
    prompt = f"""
请从以下文本中提取出所有的政策条款，只保留条款内容，去除其他说明性或背景性的文字。
要求：
- 每个条款单独一行
- 不要编号、不要标题
- 提取完整的一条政策内容，在一条政策内容中不需要删减内容
- 返回纯文本，不加解释

以下是政策文本：
{text}
"""

    try:
        response = Generation.call(
            model="qwen-turbo",  # 可选 qwen-plus / qwen-turbo
            prompt=prompt,
            request_timeout=600
        )
        clauses_text = response.output.text.strip()
        clauses = [line.strip() for line in clauses_text.splitlines() if line.strip()]
        return clauses
    except Exception as e:
        print(f"调用 Qwen 失败: {e}")
        return []


def num_to_chinese(num):
    """
    将阿拉伯数字转换为中文序数词
    """
    chinese_num = {
        1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
        6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
    }
    if num <= 10:
        return chinese_num[num]
    elif num < 20:
        return "十" + ("" if num == 10 else chinese_num[num - 10])
    elif num < 100:
        tens = num // 10
        units = num % 10
        return chinese_num[tens] + "十" + ("" if units == 0 else chinese_num[units])
    else:
        return str(num)  # 如果超过支持范围，返回原始数字


def add_numbering(clauses):
    """
    为每条政策添加中文序号前缀
    """
    return [f"{num_to_chinese(i)}、{clause}" for i, clause in enumerate(clauses, start=1)]


def extract_and_save_policy_clauses(file_path):
    """
    主函数：提取政策条款并保存为文件
    """
    print(f"开始处理文件: {file_path}")

    # 1. 加载文档内容
    documents = general_file_loader(file_path)
    raw_text = "\n".join([doc.page_content for doc in documents])

    # 2. 调用大模型提取条款
    print("正在调用千问大模型提取政策条款...")
    clauses = extract_policy_clauses_with_qwen(raw_text)

    # 3. 添加序号
    numbered_clauses = add_numbering(clauses)

    # 4. 构造输出文件名
    output_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_file = os.path.join(output_dir, f"{name_without_ext}_cl.txt")

    # 5. 保存结果
    with open(output_file, "w", encoding="utf-8") as f:
        for clause in numbered_clauses:
            f.write(clause + "\n")

    print(f"共提取 {len(clauses)} 条政策条款，已保存至 {output_file}")
    return output_file


def process_directory(root_dir):
    """
    遍历根目录中的所有文件，找到其中的txt，docx，pdf文件都进行处理，
    跳过以 _cl.txt 结尾的文件。
    """
    root_dir="D:/ProcessedFiles"
    print(f"开始遍历目录: {root_dir}")
    supported_extensions = ('.txt', '.docx', '.pdf')

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(supported_extensions):
                # 检查是否以 _cl.txt 结尾
                if file_lower.endswith('_cl.txt'):
                    print(f"跳过已处理文件: {file}")
                    continue

                file_path = os.path.join(subdir, file)
                try:
                    extract_and_save_policy_clauses(file_path)
                except Exception as e:
                    print(f"处理文件失败: {file_path}，错误：{e}")

def create_documents_from_sections(sections):
    return [Document(page_content=section) for section in sections]