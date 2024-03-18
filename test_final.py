# 使用背景 :
# 可用於職場中，開會時，藉由錄音音檔獲得整場會議逐字稿
# 可用於教學中，讓學生們課程後獲得逐字稿，回顧自己不清楚的課程細節(較建議使用於語言相關課程)
# 後續變化 : 將每段音檔文字內容引導至一個 DOC，並從中獲得摘要
#from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI

# 讀取 API 金鑰
import pandas as pd


# read text file into pandas DataFrame
df = pd.read_csv("./key.txt", sep=" ")
key = df.columns
OpenAI.api_key = key[0]

# 讀取 API 金鑰
#with open("./key.txt") as file:
#    key = file.read()
#keyfile = Path("./key.txt")
#key = keyfile.read_text()

#openai.api_key = key
#client = OpenAI(api_key = key )


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

for i in range(NUM):
    print("讀取 seg_",i,"檔")
    filename = f"seg_{i}.wav"
    audio_file= open(filename, "rb") # 使用 "rb" 模式打開檔案時，將以二進位格式讀取檔案的內容，而不會將其解釋為文字或其他形式的資料。

    # 開始使用 Whisper 模型中的 transcription 函式來轉錄音檔
    transcription = OpenAI.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    print(transcription.text)
