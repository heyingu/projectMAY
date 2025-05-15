# -*- coding: utf-8 -*-
from langchain.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain.docstore.document import Document
from .text_splitter import split_policy_documents

def load_special_document(file_path="laws.txt"):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    raw_text = documents[0].page_content if documents else ""
    return raw_text

def general_file_loader(file_path):
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    return loader.load()

def create_documents_from_sections(sections):
    return [Document(page_content=section) for section in sections]