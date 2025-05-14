import os
import tempfile
from docx import Document
import streamlit as st
from langchain.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

# 设置页面配置
st.set_page_config(
    page_title="公平竞争审查智能分析系统",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 自定义CSS样式
def set_custom_style():
    st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    .result-box {
        border-left: 4px solid #3498db;
        padding: 1.5rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin-top: 1.5rem;
    }
    .progress-text {
        font-size: 1rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .file-uploader {
        border: 2px dashed #bdc3c7;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)


set_custom_style()


# ================== 功能函数 ==================

# ================== 1. 加载并切分文档 ==================
def load_and_split_documents(file_path):
    try:
        if file_path.endswith('.txt'):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            loader = UnstructuredFileLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        return docs
    except Exception as e:
        st.error(f"文档加载错误: {e}")
        raise

# ================== 2. 初始化 Embedding 模型 ==================
def get_embeddings():
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    return HuggingFaceEmbeddings(model_name=model_name)

# ================== 3. 构建向量数据库 ==================
def build_vectorstore(docs, embeddings):
    return FAISS.from_documents(docs, embeddings)

# ================== 4. 初始化 Qwen LLM（Tongyi）==================
def get_llm(api_key):
    os.environ["DASHSCOPE_API_KEY"] = api_key
    return Tongyi(model_name="qwen-max")

# ================== 5. 定义 Prompt 模板 ==================
def get_prompt_template():
    template = """用户问题：{question}

相关法律条文：{context}

请从以下几个方面分析该政策是否违反公平竞争原则：
1. 是否限制商品、要素自由流动
2. 是否设置不合理或歧视性准入条件
3. 是否违反相关法律法规的具体条款

最后给出综合判断和建议：
"""
    return PromptTemplate(template=template, input_variables=["question", "context"])


def build_qa_chain(vectorstore, llm, prompt):
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )


def create_report_text(result):
    report = f"# 公平竞争审查智能分析报告\n\n## 分析结果\n{result}\n\n"
    return report


# ================== 主界面 ==================
def main():
    # 标题和介绍
    st.markdown('<h1 class="main-title">公平竞争审查智能分析系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">基于AI技术的政策合规性分析工具，助力公平竞争环境建设</p>', unsafe_allow_html=True)

    # 侧边栏设置
    with st.sidebar:
        st.header("⚙️ 系统设置")
        api_key = st.text_input("DashScope API Key", type="password",
                                help="请输入阿里云DashScope的API Key以启用AI分析功能")

        st.markdown("---")
        st.markdown("### 📌 使用说明")
        st.markdown("""
        1. 输入API Key (必填)
        2. 上传文件或输入政策内容
        3. 点击"开始分析"按钮
        4. 查看详细分析结果
        """)

        st.markdown("---")
        st.markdown("### 📁 支持文件格式")
        st.markdown("- 文本文件 (.txt)")
        st.markdown("- Word文档 (.docx)")
        st.markdown("- PDF文件 (.pdf)")

        st.markdown("---")
        st.markdown("""
        <div style="font-size:12px; color:#888;">
        注意：本工具分析结果仅供参考，不构成法律意见
        </div>
        """, unsafe_allow_html=True)

    # 主内容区
    tab1, tab2 = st.tabs(["📄 文件分析", "✍️ 文本输入"])

    with tab1:
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("选择或拖拽文件到此处", type=["txt", "pdf", "docx"],
                                         label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        user_question = st.text_area("在此输入政策内容...", height=200,
                                     placeholder="例：某地要求外地企业必须在本地设立分支机构才能参与招投标",
                                     label_visibility="collapsed")

    # 分析按钮
    if st.button("🚀 开始分析", use_container_width=True):
        if not api_key:
            st.error("请先输入有效的API Key！")
            st.stop()

        if not uploaded_file and not user_question.strip():
            st.error("请上传文件或输入政策内容！")
            st.stop()

        # 创建进度指示器
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 步骤1：处理输入
        with st.spinner("准备分析数据..."):
            status_text.markdown("**🔄 正在处理输入内容...**")
            progress_bar.progress(10)

            try:
                if uploaded_file:
                    # 保存上传文件到临时文件
                    with tempfile.NamedTemporaryFile(delete=False,
                                                     suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        file_path = tmp.name
                    docs = load_and_split_documents(file_path)
                    os.unlink(file_path)  # 删除临时文件
                else:
                    if user_question.strip():
                        docs = [Document(page_content=user_question)]
                    else:
                        docs = []

                progress_bar.progress(20)
            except Exception as e:
                st.error(f"数据处理失败: {str(e)}")
                st.stop()

        # 检查是否有文档
        if not docs:
            st.error("无法加载任何文档内容，请检查输入。")
            st.stop()

        # 步骤2-6：执行分析流程
        steps = [
            ("🔍 加载语义分析模型", 30),
            ("🧠 构建知识库", 50),
            ("🤖 初始化AI引擎", 70),
            ("💡 生成分析模板", 85),
            ("⚡ 执行智能分析", 95)
        ]

        result = ""
        try:
            for step, progress in steps:
                status_text.markdown(f"**{step}...**")
                progress_bar.progress(progress)

                if step == steps[0][0]:
                    embeddings = get_embeddings()
                elif step == steps[1][0]:
                    vectorstore = build_vectorstore(docs, embeddings)
                elif step == steps[2][0]:
                    llm = get_llm(api_key)
                elif step == steps[3][0]:
                    prompt = get_prompt_template()
                elif step == steps[4][0]:
                    qa_chain = build_qa_chain(vectorstore, llm, prompt)
                    query = user_question if user_question.strip() else "请分析该政策是否符合公平竞争原则"
                    result = qa_chain.run(query)

            progress_bar.progress(100)
            status_text.success("✅ 分析完成！")

            # 显示结果
            st.markdown("---")
            st.subheader("📋 分析报告")

            # 美化结果显示
            report_text = create_report_text(result)
            st.markdown(f"""
            <div class="result-box">
            {report_text}
            """, unsafe_allow_html=True)

        except Exception as e:
            progress_bar.progress(0)
            status_text.error(f"分析过程中出错: {str(e)}")


if __name__ == "__main__":
    main()



