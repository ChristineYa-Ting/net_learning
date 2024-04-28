from pathlib import Path
from datetime import datetime, timedelta
import random
from pydub import AudioSegment
from openai import OpenAI
from transformers import pipeline
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time


#from huggingface_hub import notebook

# 讀取 API 金鑰
keyfile = Path("./key.txt")
key = keyfile.read_text()
OpenAI.api_key = key

client = OpenAI(api_key = key)

# 讀取音訊檔案
audio = AudioSegment.from_file("./EarningsCall.wav")

# 定義分割大小（這裡以每段 60 秒為例）
SEGMENT_LENGTH_MS = 60000

# 分割音訊檔案
segments = []
NUM = 0  # 設定變數用於記錄分割的片段數量
for start_time in range(0, len(audio), SEGMENT_LENGTH_MS):
    segment = audio[start_time:start_time + SEGMENT_LENGTH_MS]
    segments.append(segment) # 將分割出的音訊片段加入到一個名為 segments 的列表中，對應 segments = []
    NUM += 1

# 將分割後的音訊檔案儲存到新的檔案中
# 運用 enumerate() 函式，從 segment 列表中會取出各元素的索引值和對應值
for i, segment in enumerate(segments):
    segment.export(f"seg_{i}.wav", format="wav")

doc = []
for i in range(NUM):
    print("讀取 seg_",i,"檔")
    filename = f"seg_{i}.wav"
    audio_file= open(filename, "rb") # 使用 "rb" 模式打開檔案時，將以二進位格式讀取檔案的內容，而不會將其解釋為文字或其他形式的資料。

    # 開始使用 Whisper 模型中的 transcription 函式來轉錄音檔
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    #print(transcription)
    doc.append(transcription)

# 将所有 transcriptions 合併成一個文檔
Merge_Document = "".join(doc)

# 将合併後的文檔組成一個文件
with open("merged_text.txt", "w", encoding="utf-8") as file:
    file.write(str(Merge_Document))

#-------------------------------------------------------------------------------

# huggingface : https://huggingface.co/knkarthick/MEETING_SUMMARY
summarizer = pipeline("summarization", model="knkarthick/MEETING_SUMMARY")
with open("merged_text.txt", "r", encoding="utf-8") as file:
    merged_text = file.read()

print(summarizer(merged_text))
summary = str(summarizer(merged_text))

#-------------------------------------------------------------------------------

# 設定 Google Sheets 的憑證
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)

# 開啟 Google Sheets 試算表
sheet = client.open_by_key("1rGfEcGu6d2oYrSpuSP3hmLRGsTHX7uvivlozJEiBtbE").sheet1

# 獲取人員的數量
num_personnel = len(sheet.col_values(2)) - 1  # 減去表頭的一行

# 獲取當天日期並轉換為所需的格式
today = datetime.now().strftime('%Y-%m-%d')

# 生成隨機的會議時間和時長，並填入表格中
for i in range(2, num_personnel + 2):  # 從第二行開始填入，因為第一行是表頭
    meeting_time = datetime.now().replace(hour=random.randint(9, 18), minute=0, second=0, microsecond=0)  # 隨機生成會議時間
    meeting_duration = random.randint(30, 120)  # 隨機生成會議時長，單位為分鐘

    # 填入表格中
    sheet.update_cell(i, 3, today)  # 填入當天日期
    sheet.update_cell(i, 4, str(meeting_time.strftime('%H:%M')) + '-' + str((meeting_time + timedelta(minutes=meeting_duration)).strftime('%H:%M')))  # 填入會議時間和時長

print("模擬資料已成功填入 Google Sheets 文件中！")

data = sheet.get_all_records()

# 定義工作時間範圍
start_time = datetime.strptime('09:00', '%H:%M')
end_time = datetime.strptime('18:00', '%H:%M')

# 使用者輸入會議時長和參加員工姓名
meeting_duration1 = int(input("請輸入會議時長（分鐘）："))
print("請逐行輸入參加新會議的員工姓名，每行一個姓名。輸入完畢後輸入一個空行以結束。")
participants = []
while True:
    participant = input("員工姓名：").strip()
    if not participant:  # 如果輸入的是空行，結束輸入
        break
    participants.append(participant)

# 從 Google Sheets 中獲取參與者的日程
def get_schedule(participant_name):
    participant_schedule = []
    for row in data:
        if row['員工姓名'] == participant_name:
            # 將會議時間轉換為 datetime 物件
            start_time_str, end_time_str = row['會議時間'].split('-')
            start_time_person = datetime.strptime(start_time_str, '%H:%M')
            end_time_person = datetime.strptime(end_time_str, '%H:%M')
            participant_schedule.append((start_time_person, end_time_person))
    return participant_schedule

# 尋找可行的會議時間
available_times = []
current_time = start_time
while current_time + timedelta(minutes=meeting_duration1) <= end_time:
    is_available = True
    for participant in participants:
        # 獲取參與者的日程
        participant_schedule = get_schedule(participant)
        # 檢查新會議時間是否與參與者的日程衝突
        for schedule_start, schedule_end in participant_schedule:
            if current_time < schedule_end and current_time + timedelta(minutes=meeting_duration1) > schedule_start:
                is_available = False
                break
        if not is_available:
            break

    if is_available:
        available_times.append((current_time, current_time + timedelta(minutes=meeting_duration1)))

    current_time += timedelta(minutes=15)   # 每次增加 15 分鐘

# 輸出可行的會議時間
if not available_times:
    print("抱歉，參與者目前無可行會議時間，請重新開始 ! ")
    exit()
else:
    print("可行的會議時間：")
    for start, end in available_times:
        print(f"{start.strftime('%H:%M')} 到 {end.strftime('%H:%M')}")


# 開啟 Google Sheets 試算表
worksheet = client.open_by_key("1rGfEcGu6d2oYrSpuSP3hmLRGsTHX7uvivlozJEiBtbE").get_worksheet(1)
meeting_strtime = input("請輸入會議開始時間 : ")

# 尋找第一個空列的位置
empty_row = 1
while worksheet.cell(empty_row, 1).value:
    empty_row += 1

# 將會議時間範圍寫入 Google Sheets
worksheet.update_cell(empty_row, 1, today + '  ' + meeting_strtime + '-' + (datetime.strptime(meeting_strtime, '%H:%M') + timedelta(minutes=meeting_duration1)).strftime('%H:%M'))

# 將參加人員資訊轉換為字串並寫入 Google Sheets
participants_str = ', '.join(participants)
worksheet.update_cell(empty_row, 2, participants_str)


worksheet.update_cell(empty_row, 3, summary)


#-------------------------------------------------------------------------------
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
rag_chain = (
    {"context": retriever | format_data, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


user_ques = input("請輸入問題 : ")
result= rag_chain.invoke(user_ques)
print(result)


#-------------------------------------------------------------------------------
RAGsheet = client.open_by_key("1rGfEcGu6d2oYrSpuSP3hmLRGsTHX7uvivlozJEiBtbE").get_worksheet(2)

# 尋找第一個空列的位置
RAG_empty_row = 1
while RAGsheet.cell(RAG_empty_row, 1).value:
    RAG_empty_row += 1

RAG_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))

RAGsheet.update_cell(RAG_empty_row, 1, RAG_time)
RAGsheet.update_cell(RAG_empty_row, 2, user_ques)
RAGsheet.update_cell(RAG_empty_row, 3, result)
