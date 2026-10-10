# 基streamlit完成WEB网页上传服务
# streamlit: 当WEB页面元素发生变化，则代码重新执行一遍，会导致状态的丢失
import time

import streamlit as st
from knowlwdge_base import KnowledgeBaseService

# 添加网页标题
st.title("知识库更新服务")

# file_uploader  文件上传框
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=["txt"],
    accept_multiple_files = False,  # False表示仅接受一个文件的上传
)

# streamlist 提出 session_state 解决状态丢失 是一个字典
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    # 提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024  # 单位大小KB

    st.subheader(f"文件名:{file_name}")  # 小一级标题
    st.write(f"格式:{file_type}| 大小：{file_size:.2f} KB")  # 正常大小的文本

    # 获取文件内容 get_value-> bytes-> decode('utf-8')
    text = uploader_file.getvalue().decode("utf-8")
    # st.write(text)

    with st.spinner("载入知识库中..."):  # 转圈动画，提高体验感
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text,file_name)  # 都传进去
        st.write(result)
