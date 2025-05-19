from langchain_community.document_loaders import TextLoader  # 假设这是正确的导入路径
# 如果 Docx2txtLoader 和 PyPDFLoader 需要从其他地方导入，请根据实际情况调整
import os
import requests
import tempfile


# 假设之前的 general_file_loader 定义在这里
# 配置 olmOCR 服务地址（假设你已经在本地启动了 olmOCR 的 API）
OLMOCR_API_URL = "http://127.0.0.1:8000/ocr"  # 示例地址，请根据实际情况修改


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
def test_general_file_loader_with_pdf(pdf_path):
    """
    测试 general_file_loader 函数能否正确处理 PDF 文件。
    """
    try:
        documents = general_file_loader(pdf_path)
        print("文档加载成功！")
        for doc in documents:
            print(f"内容片段: {doc.page_content}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    # 示例：使用一个现有的 PDF 文件进行测试
    # 请替换为你自己的 PDF 文件路径
    pdf_test_file_path = r"/aaa/政策二.pdf"

    if not os.path.exists(pdf_test_file_path):
        print("指定的 PDF 文件不存在，请检查路径后重试。")
    else:
        test_general_file_loader_with_pdf(pdf_test_file_path)