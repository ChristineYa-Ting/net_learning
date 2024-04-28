## 網路輔助學習系統研究 ##

**製作者:張雅婷**


**指導教授:蔡芸琤**


**學系:臺灣師範大學科技應用與人力資源發展學系人資組**


**🔖 ChatGPT API Pratice**
------------------------------
🔗Code: [0318_Practice.py](https://github.com/ChristineYa-Ting/net_learning/blob/main/0318_Practice.py)

👉可用於職場中，開會時，藉由錄音音檔獲得整場會議逐字稿  
👉可用於教學中，讓學生們課程後獲得逐字稿，回顧自己不清楚的課程細節(較建議使用於語言相關課程)

<details> 
  <summary> Code Result :  </summary>
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0318_Result.png)
  
</details>



**🛒 Hubspot Model Pratice**
------------------------------
🔗Code : [0401_Practice.py](https://github.com/ChristineYa-Ting/net_learning/blob/main/0401_Practice.py)

接續上篇的練習，增加 Hubspot 的文件重點摘要、問答的功能

<details> 
  <summary> Code Result :  </summary>
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0401_Result.png)
  
</details>



**💫 RAG (OpenAI) Pratice**
------------------------------
🔗Code : [0415_Practice.py](https://github.com/ChristineYa-Ting/net_learning/blob/main/0415_Practice.py)

使用 RAG 打造針對整篇逐字稿的問答模型

<details> 
  <summary> Code Result :  </summary>
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0415_Result.png)
  
</details>



**📑 Google sheet API Pratice**
----------------------------------
🔗Code : [0429_Practice.py](https://github.com/ChristineYa-Ting/net_learning/blob/main/0429_Practice.py)

使用 Google sheet 雲端共編串接至 vscode 進行數位孿生設計

運用情境 :
1. 模擬建立各個員工當日已有的會議時間 (會顯示於 google sheet 1)
2. 秘書可填入想要的會議時長、參加人員，系統將提供可預約的會議時間
3. 輸入選擇的會議時間後，會將其會議時間、參與人員自動填入到 google sheet 2 

<details> 
  <summary> Code Result :  </summary>
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0429_result.png)
  
</details>

<details> 
  <summary> Sheet Result :  </summary>

  #### google sheet 1 : ####
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0429_google%20sheet%201.png)

  #### google sheet 2 : ####
  
  ![Picture](https://github.com/ChristineYa-Ting/net_learning/blob/main/Result_Picture/0429_google%20sheet%202.png)
  
</details>




**🚩🚩 Whole Integrate 01 🚩🚩**
--------------------------------------------
🔗Code : [0429_Whole_Integrate.py](https://github.com/ChristineYa-Ting/net_learning/blob/main/0429_Whole_Integrate.py)

將前面所學全部串接一起

流程如下 :
1. 串接 OpenAI API 金鑰
   
   (1). 將會議音訊檔進行每 60 秒分割(避免音檔太大而無法執行)，並將分割檔另存為 seg_i 檔

   (2). 使用 Whisper 模型中的 transcription 函式來轉錄音檔，進行每個分割檔的逐字稿讀取

   (3). 將所有的轉錄之逐字稿合併成一個文檔，並輸出為 merged_text.txt 的文件

2. 串接 HuggingFace Model ， 根據逐字稿(merged_text.txt) 進行摘要
3. 串接 google sheet API

   (1). 模擬建立各個員工當日已有的會議時間 (會顯示於 google sheet 1)

   (2). 秘書可填入想要的會議時長、參加人員，系統將提供可預約的會議時間

   (3). 輸入選擇的會議時間後，會將其**會議時間、參與人員、會議內容摘要**自動填入到 google sheet 2 

4. 回到 OpenAI RAG LLM 模型

   (1). TextLoader 對象為逐字稿(merged_text.txt)

   (2). 進行文本分割、檢索和生成

   (3). 提供使用者輸入問題，系統會根據逐字稿內容進行回答

5. 回到 google sheet API
   
   (1). 讀取 google sheet 3

   (2). 將上述之問題和回答自動匯入至 google sheet 3



