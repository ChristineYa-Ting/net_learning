#參考資料 : https://www.learncodewithmike.com/2020/08/python-write-to-google-sheet.html
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random

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
