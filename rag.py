import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableParallel, RunnableLambda

api_key = os.getenv("DASHSCOPE_API_KEY")

from vector_stores import VectorStoreService
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.documents import Document
from file_history_store import get_history

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class RagService(object):

    def __init__(self):

        # 四个核心成员变量
        #向量服务类 创建类的实例对象
        self.vector_service = VectorStoreService(
            embedding = DashScopeEmbeddings(model=config.embedding_model_name,dashscope_api_key=api_key),
        )
        # 提示词模版类 创建类的实例对象
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system","以我提供的已知参考资料为主，"
                 "简洁和专业的回答用户问题。参考资料：{context}。"),
                ("system","并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder("history"),
                ("user","请回答用户提问：{input}"),
            ]
        )
        # 聊天模型
        self.chat_model = ChatTongyi(model = config.chat_model_name,streaming=True)
        # 链来自于方法get_chain的返回值
        self.chain = self.__get_chain()


    def __get_chain(self):
        """获取最终的执行链"""
        # 检索器对象
        retriever = self.vector_service.get_retriever()

        def format_decument(docs:list[Document]):  # 组装成字符串
            if not docs:
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def format_for_retriever(value:dict) -> str:  # retriever 输入为字符串
            return value["input"]

        def format_for_prompt_template(value):  # 找 history 位置
            # {input,context,history}
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        chain = (
            {
                "input":RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_decument  # 将用户的输入给了检索器retriever，检索器通过我们的向量存储获取到参考资料，拿到参考资料后把它提供给format_document函数组装成字符串
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain


if __name__ == "__main__":
    # session id 配置
    session_config = {
        "configurable":{
            "session_id":"user_001",
        }
    }
    res = RagService().chain.invoke({"input":"针织毛衣如何保养"}, session_config)
    print(res)