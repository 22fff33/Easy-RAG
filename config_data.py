# 配置变量
from networkx.algorithms import similarity

# md5_path = "./md5.text"
#
# # Chroma
collection_name = "rag"
# persist_directory = "./chroma_db"

import os

# 获取 config_data.py 这个文件所在的绝对文件夹路径（也就是 D:\PythonProject7\RAG）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 将所有相对路径改为基于 BASE_DIR 的绝对路径
persist_directory = os.path.join(BASE_DIR, "chroma_db")   # 向量数据库文件夹路径
md5_path = os.path.join(BASE_DIR, "md5.txt")

# spliter
chunk_size = 1000
chunk_overlap = 100
max_split_char_number = 1000  # 文本分割的阈值
separators = [" ", "\t", "\n", "\r", "", "\n\n", "!", "?","！", "？", ",", ".", "，", "。"]

# 检索返回匹配的文档数量
similarity_threshold = 1

# 模型
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3.7-max"

session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}