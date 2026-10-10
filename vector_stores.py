#向量存储
from langchain_chroma import Chroma
import config_data as config

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
# 构建检索库
class VectorStoreService(object):

    def __init__(self,embedding):  # 传入文本转向量的模型

        self.embedding = embedding

        # 向量存储的实例
        self.vector_store = Chroma(
            collection_name = config.collection_name,
            embedding_function = self.embedding,
            persist_directory = config.persist_directory,
        )

    # 返回向量检索器，方便加入chain
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs = {"k": config.similarity_threshold})



if __name__ == "__main__":
    from langchain_community.embeddings import DashScopeEmbeddings

    retriever = VectorStoreService(DashScopeEmbeddings(model = "text-embedding-v4",dashscope_api_key=api_key)).get_retriever()

    res = retriever.invoke("我的体重150斤，尺码推荐")
    print(res)