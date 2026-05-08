import tkinter as tk
from datetime import date

def check_stage(event=None):
    birth = entry.get().replace(' ', '').replace('-', '').replace('.', '')
    
    # 4자리(YYMM) 입력 처리
    if len(birth) == 4 and birth.isdigit():
        yy = int(birth[:2])
        month = int(birth[2:])
        current_year_short = date.today().year % 100
        # 26년(현재)보다 크면 1900년대, 작거나 같으면 2000년대로 판단
        year = 1900 + yy if yy > current_year_short + 1 else 2000 + yy
            
    elif len(birth) == 6 and birth.isdigit():
        year = int(birth[:4])
        month = int(birth[4:])
    else:
        result_label.config(text="형식 오류\n(예: 2402)", fg="#d32f2f")
        return

    if not (1 <= month <= 12):
        result_label.config(text="월 입력 오류\n(1~12월 사이)", fg="#d32f2f")
        return

    today = date.today()
    months_old = (today.year - year) * 12 + (today.month - month)

    if months_old < 0:
        result_label.config(text="미래에서 오셨나요?\n아직 태어나지 않았어요!", fg="#d32f2f")
        return

    # --- 어르신 및 단계 판별 로직 ---
    if months_old >= 228: # 19세 이상 (2007년생 포함 이전)
        result_label.config(text=f"{months_old}개월 / 어르신...??", fg="#4e342e")
    elif year > 2024 or (year == 2024 and month >= 11):
        result_label.config(text=f"{months_old}개월 / 수령 가능!\n1단계", fg="#1976d2")
    elif (year == 2024 and month <= 10) or (year == 2023 and month >= 6):
        result_label.config(text=f"{months_old}개월 / 수령 가능!\n2단계", fg="#1976d2")
    elif (year == 2023 and month <= 5) or (2020 <= year <= 2022):
        result_label.config(text=f"{months_old}개월 / 수령 가능!\n3단계", fg="#1976d2")
    else:
        # 학교 간 어린이들 (대략 7세~18세 사이)
        result_label.config(text=f"{months_old}개월 / 초등학생 이상\n학교를 간 아가는 아가가 아니다!", fg="#d32f2f")

# UI 설정
root = tk.Tk()
root.title("북스타트 계산기")
root.geometry("300x180")
root.attributes('-topmost', True)

tk.Label(root, text="생년월일 입력 (예: 2404)", font=("맑은 고딕", 10)).pack(pady=(15, 0))

entry = tk.Entry(root, width=12, justify='center', font=("맑은 고딕", 14))
entry.pack(pady=10)
entry.focus_set()
entry.bind('<Return>', check_stage)

# wraplength=250으로 글자가 길면 자동 줄바꿈
result_label = tk.Label(root, text="날짜를 입력해주세요", font=("맑은 고딕", 11, "bold"), wraplength=250)
result_label.pack(pady=5)

root.mainloop()