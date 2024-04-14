# https://python.langchain.com/docs/use_cases/question_answering/quickstart/#retrieval-and-generation-generate
# https://smith.langchain.com/hub/rlm/rag-prompt
#import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

#os.environ["key.txt"] = getpass.getpass()
# 從文件中讀取 API 密鑰
with open("key.txt", "r", encoding="utf-8") as file:
    api_key = file.read().strip()

# 設置 API 密鑰
os.environ["OPENAI_API_KEY"] = api_key

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# 創建 TextLoader 對象，指定 TXT 檔路徑
loader = TextLoader("merged_text.txt")
data = loader.load()

# (分割)
# 定義名為 RecursiveCharacterTextSplitter 的文本分割器，將文本資料分割成長度為 1000 字元的片段，這些片段之間會有 200 字元的重疊。
# 使用分割器來將文檔進行分割，將分割後的結果儲存在 splits 中
# 使用分割後文檔來建立名為 Chroma 的向量儲存庫，並使用 OpenAI 的嵌入技術將文本嵌入到向量空間中
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(data)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())


# (檢索)
# 定義名為 retriever 的檢索器，它可從向量儲存庫中檢索相關的文檔
# 當 Chroma 中的文件數量有限時，會發生 {Number of requested results 4 is greater than number of elements in index 3, updating n_results = 3}
# 預設情況下，擷取器使用similarity_search，其預設值為k=4，為解決錯誤，需調整檢索器的參數
# 定義 prompt (一個預訓練好的模型，用於生成回答)
# format_data 函式被定義用來將文檔格式化成特定的形式
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
prompt = hub.pull("rlm/rag-prompt")
def format_data(data):
    return "\n\n".join(doc.page_content for doc in data)

# (檢索和生成)
# 定義 rag_chain，這是一個問答鏈，它接收一個問題，然後根據前面定義的檢索器和格式化函式來提供回答
#user_question = input("請輸入您的問題：")
rag_chain = (
    {"context": retriever | format_data, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

result = rag_chain.invoke("How much is the EBITDA martin ?")
print(result)
