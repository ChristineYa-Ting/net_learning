# 使用背景
# 可用於職場中，開會時，藉由錄音音檔獲得整場會議逐字稿
# 可用於教學中，讓學生們課程後獲得逐字稿，回顧自己不清楚的課程細節(較建議使用於語言相關課程)
# 後續變化 : 將每段音檔文字內容引導至一個 DOC，並從中獲得摘要
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModelForQuestionAnswering
import torch
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

    print(transcription)
    doc.append(transcription)

# 将所有 transcriptions 合併成一個文檔
Merge_Document = "".join(doc)

# 将合併後的文檔組成一個文件
with open("merged_text.txt", "w", encoding="utf-8") as file:
    file.write(str(Merge_Document))

# huggingface : https://huggingface.co/knkarthick/MEETING_SUMMARY
summarizer = pipeline("summarization", model="knkarthick/MEETING_SUMMARY")
with open("merged_text.txt", "r", encoding="utf-8") as file:
    merged_text = file.read()

print(summarizer(merged_text))

# huggingface : https://huggingface.co/Intel/dynamic_tinybert?context=In+the+second+quarter+of+this+year%2C+FinTech+Plus+saw+a+25%25+increase+in+revenue+to+%24125+million+and+a+30%25+EBITDA+margin+to+%2437.5+million.+Net+income+rose+to+%2416+million%2C+which+is+a+significant+increase+from+%2410+million+in+Q2&text=How+much+is+Q2+revenue
# 使用 Hugging Face Transformers 中, AutoTokenizer 的訓練模型 "Intel/dynamic_tinybert" ，並命為 tokenizer 變項
tokenizer = AutoTokenizer.from_pretrained("Intel/dynamic_tinybert")
# 使用 AutoModelForQuestionAnswering 的訓練模型 "Intel/dynamic_tinybert" 中載入一個問答模型。
model = AutoModelForQuestionAnswering.from_pretrained("Intel/dynamic_tinybert")

CONT = str(summarizer(merged_text))  # 背景情境
QUES = "How much is the revenue in Q2 ?"  # 詢問的問題

# Tokenize the context and question
# 將背景與問題進行編碼，並返回 PyTorch 張量，truncation=True 表示如果超過了 tokenizer 的最大長度，將會截斷文本
tokens = tokenizer.encode_plus(QUES, CONT, return_tensors="pt", truncation=True)

# Get the input IDs and attention mask (用模型進行問答，傳入了問題和摘要的 input_ids 和 attention_mask)
input_ids = tokens["input_ids"]
attention_mask = tokens["attention_mask"]

# Perform question answering (通过分析起始位置得分和结束位置得分，可确定答案在给定上下文中的起始和结束位置，從中提取答案)
outputs = model(input_ids, attention_mask=attention_mask)
start_scores = outputs.start_logits
end_scores = outputs.end_logits

# Find the start and end positions of the answer
answer_start = torch.argmax(start_scores)
answer_end = torch.argmax(end_scores) + 1
ans = tokenizer.convert_tokens_to_string(
    tokenizer.convert_ids_to_tokens(input_ids[0][answer_start:answer_end]))
# 將模型的輸出中包含的 token ids 轉換回字串形式的答案，並將其存儲在變數 ans 中

# Print the answer
print("Answer:", ans)
