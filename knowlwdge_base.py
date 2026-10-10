# 知识库
# 离线

from dotenv import load_dotenv
load_dotenv()
import hashlib
import os
import config_data as config  # 自己设置的环境变量
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

api_key = os.getenv("DASHSCOPE_API_KEY")

def check_md5(md5_str: str):
    """
    检查传入的md5字符串是否已经被处理过了
    return False 未处理  True 已经处理过，已有记录
    """
    if not os.path.exists(config.md5_path):  # if 进入表示文件不存在，肯定没有处理过
        open(config.md5_path, 'w', encoding="utf-8").close()  # 建一个空文件
        return False  # 未处理过
    else:
        for line in open(config.md5_path, 'r', encoding="utf-8").readlines():
            line = line.strip()
            if line == md5_str:
                return True  # 已处理过

        return False  # 未处理过


def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding = "utf-8"):
    """将传入的字符串转换成md5字符串"""

    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding = encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()  # 得到md5对象
    md5_obj.update(str_bytes)  # 更新内容（传入即将要转换的字节数组）
    med_hex = md5_obj.hexdigest()  # 得到md5的十六制字符串

    return med_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name = config.collection_name,  # 数据库的表名
            embedding_function = DashScopeEmbeddings(model="text-embedding-v4",dashscope_api_key=api_key),  # 使用的模型
            persist_directory = config.persist_directory,  # 数据库本地存储文件夹
        )  # 向量存储的实例  Chroma向量对象

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = config.chunk_size,  # 分割后的文本段最大长度
            chunk_overlap = config.chunk_overlap,   # 连续文本段之间的字符重叠数量
            separators = config.separators,  # 自然段落划分的符号
            length_function = len,   # 使用Python自带的len函数做长度统计的依据
        )  # 文本分割器的对象

    def upload_by_str(self,data: str, filename):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        # 先得到传入字符串的md5
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"小村庄",
        }

        self.chroma.add_texts(  # 内容就加载到向量库中了
            knowledge_chunks,
            metadata = [metadata for _ in knowledge_chunks],
        )

        save_md5(md5_hex)  # 将处理的保存

        return "[成功]内容已经成功载入向量库"

# if __name__ == "__main__":
#     service = KnowledgeBaseService()
#     r = service.upload_by_str("刘若楠","testfile")
#     print(r)