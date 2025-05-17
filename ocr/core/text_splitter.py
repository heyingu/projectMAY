# -*- coding: utf-8 -*-
import re
from config import config

def split_policy_documents(text):
    pattern = r"(一|二|三|四|五|六|七|八|九|十、|$[一二三四五六七八九十]$)"
    sections = re.split(pattern, text)
    
    result = []
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            title = sections[i] + sections[i + 1]
            if title.strip():
                result.append(title.strip())
    return result[:config.MAX_POLICIES]

class RecursiveTextSplitter:
    def __init__(self):
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len
        )
    
    def split_text(self, text):
        return self.splitter.split_text(text)