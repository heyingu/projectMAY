import streamlit as st
import os
from pathlib import Path
import urllib.parse
import dashscope
# 假设 main 函数已重构为可接受输入目录并返回结果
from core.maint import process_directory_and_get_results


# os.environ["DASHSCOPE_API_KEY"] = 'sk-96c664f8b1194cdf91d94148c4d9d8f6'
# MONGODB_URI = "mongodb://readonly_user:wyx123@10.234.176.114:27017/?authSource=公平竞争规则"
#

# print("当前环境变量中的API Key:", os.getenv("DASHSCOPE_API_KEY"))
# print("Dashscope SDK 使用的API Key:", dashscope.api_key)
import shutil

def clear_directory(directory_path: Path):
    """
    清空指定目录下的所有文件和子文件夹内容，但保留该目录本身。
    """
    try:
        for item in directory_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)  # 删除子文件夹
            else:
                item.unlink()  # 删除文件
        st.info(f"已清理临时文件：{directory_path}")
    except Exception as e:
        st.warning(f"清理文件时出错：{str(e)}")
def generate_txt_report(results):
    """
    将分析结果转换为 TXT 格式
    """
    txt_content = "政策文件分析结果\n"
    txt_content += "=" * 50 + "\n\n"

    for idx, item in enumerate(results, 1):
        txt_content += f"问题 {idx}：{item['question']}\n"
        txt_content += f"回答：{item['result']}\n"
        txt_content += "-" * 50 + "\n\n"

    return txt_content.encode("utf-8")  # 转为字节流


def get_save_directory():
    """
    获取文件保存路径（优先使用 D盘，失败则回退到桌面）
    """
    # 强制指定 D盘路径（适用于 Windows）
    d_drive_path = Path("D:/ProcessedFiles")

    # 尝试创建 D盘文件夹
    try:
        d_drive_path.mkdir(exist_ok=True, parents=True)
        # 检查是否有写入权限
        test_file = d_drive_path / ".write_test"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return d_drive_path
    except Exception as e:
        print(f"无法使用 D盘路径：{str(e)}")
        # 回退到桌面路径
        if os.name == 'nt':
            desktop_path = Path(os.environ["USERPROFILE"]) / "Desktop"
        else:
            desktop_path = Path.home() / "Desktop"
        return desktop_path / "ProcessedFiles"


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
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 结果展示框 */
    .stExpander {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 1.2rem 0;
        border-left: 4px solid #3498db;
    }
    .stExpander .streamlit-expanderHeader {
        font-size: 1.2rem;
        color: #2c3e50;
        font-weight: 600;
        padding: 1rem 1.5rem; /* 增加内边距 */
    }
    .stExpander .streamlit-expanderContent {
        padding: 1.5rem; /* 增加内边距 */
        background: #f8f9fa; /* 添加背景色 */
        border-radius: 0 0 12px 12px; /* 圆角匹配容器 */
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

def main():
    # 获取文件保存路径
    processed_dir = get_save_directory()
    processed_dir.mkdir(exist_ok=True)  # 确保目录存在
    # 标题和介绍
    st.markdown('<h1 class="main-title">⚖️ 公平竞争审查智能分析系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">基于AI技术的政策合规性分析工具，助力公平竞争环境建设</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📌 使用说明")
        st.markdown("""
        1. 请选择输入方式并上传政策文件
        2. 点击"开始分析"按钮
        3. 系统将自动完成分析并展示结果
        """)
        st.markdown("---")
        st.markdown("⚠️ 注意：AI生成内容仅供参考，请以实际政策文件为准。本系统不承担任何法律或决策责任")

    # tab1, tab2 = st.tabs(["📄 文件分析", "✍️ 文本输入"])

    uploaded_file = None
    user_text = ""

    # with tab1:
    #     input_method = "上传文件"
    #     st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
    #     uploaded_file = st.file_uploader("选择或拖拽文件到此处", type=["txt", "pdf", "docx"],
    #                                      label_visibility="collapsed")
    #     st.markdown('</div>', unsafe_allow_html=True)
    #
    # with tab2:
    #     input_method = "直接输入文本"
    #     user_question = st.text_area("在此输入政策内容...", height=200,
    #                                  placeholder="例：某地要求外地企业必须在本地设立分支机构才能参与招投标",
    #                                  label_visibility="collapsed")

    input_method = st.radio("请选择输入方式", options=["📄 文件分析", "✍️ 文本输入"])
    if input_method == "📄 文件分析":
        uploaded_file = st.file_uploader("上传政策文件", type=["txt", "docx", "pdf"])
    else:
        user_text = st.text_area("请输入政策文本", height=300)
    if st.button("🚀 开始分析", use_container_width=True):
        if input_method == "📄 文件分析" and not uploaded_file:
            st.error("请先上传文件")
        elif input_method == "✍️ 文本输入" and not user_text.strip():
            st.error("请输入文本内容")
        else:
            # 保存文件到桌面
            if input_method == "📄 文件分析":
                safe_filename = urllib.parse.quote(uploaded_file.name)  # 处理中文文件名
                file_path = processed_dir / safe_filename

                # 避免文件覆盖
                counter = 1
                while (processed_dir / file_path.name).exists():
                    name, ext = os.path.splitext(safe_filename)
                    file_path = processed_dir / f"{name}_{counter}{ext}"
                    counter += 1

                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.info(f"文件已保存至：{file_path}")
            else:
                file_path = processed_dir / "user_input.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(user_text)
                st.info(f"文本已保存至：{file_path}")

            # 调用处理函数（使用桌面路径）
            try:
                results = process_directory_and_get_results(processed_dir)
                print(results)
                if not results:
                    st.warning("未找到分析结果，请检查文件内容或处理逻辑")
                else:
                    st.success("处理完成！以下是分析结果：")
                    for idx, item in enumerate(results, 1):
                        with st.expander(f"问题 {idx}：{item['question']}"):
                            st.markdown(f"**回答：**\n{item['result']}")

                    # 生成 TXT 报告
                    txt_bytes = generate_txt_report(results)

                    # 提供下载链接
                    st.download_button(
                        label="📥 下载分析结果 TXT",
                        data=txt_bytes,
                        file_name="analysis_report.txt",
                        mime="text/plain"
                    )
                    clear_directory(processed_dir)
            except Exception as e:
                st.error(f"处理失败：{str(e)}")
                print("Error Details:", str(e))  # 打印完整错误信息

if __name__ == "__main__":
        main()