import os
import socket
import sys
import threading
import tkinter as tk
from datetime import date


# =========================
# 프로그램 기본 설정
# =========================

APP_NAME = "북스타트 계산기"
APP_VERSION = "1.0.1"
DEVELOPER_NAME = "tomepetty"
ICON_FILE = "icon.ico"

SINGLE_INSTANCE_HOST = "127.0.0.1"
SINGLE_INSTANCE_PORT = 41723

WINDOW_SIZE = "320x260"
WINDOW_MIN_SIZE = (300, 250)

COLOR_NORMAL = "#333333"
COLOR_GUIDE = "#666666"
COLOR_FOOTER = "#777777"
COLOR_SUCCESS = "#1976d2"
COLOR_ERROR = "#d32f2f"
COLOR_WARNING = "#4e342e"

FONT_GUIDE = ("맑은 고딕", 9)
FONT_INPUT = ("맑은 고딕", 15)
FONT_RESULT = ("맑은 고딕", 11, "bold")
FONT_TITLE = ("맑은 고딕", 11, "bold")
FONT_BUTTON = ("맑은 고딕", 9)
FONT_FOOTER = ("맑은 고딕", 7)


# =========================
# 파일 경로 처리
# =========================

def resource_path(relative_path):
    """PyInstaller exe에서도 포함 파일을 찾을 수 있게 경로를 만듭니다."""

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# =========================
# 중복 실행 방지
# =========================

def acquire_single_instance():
    """
    이미 실행 중인 프로그램이 있으면 기존 창에 신호를 보내고 종료합니다.
    실행 중인 프로그램이 없으면 서버 소켓을 반환합니다.
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((SINGLE_INSTANCE_HOST, SINGLE_INSTANCE_PORT))
        server_socket.listen(1)
        return server_socket
    except OSError:
        notify_existing_instance()
        sys.exit()


def notify_existing_instance():
    """이미 실행 중인 프로그램에 창을 앞으로 올리라는 신호를 보냅니다."""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SINGLE_INSTANCE_HOST, SINGLE_INSTANCE_PORT))
    except Exception:
        pass


def start_instance_listener(server_socket, on_signal):
    """두 번째 실행 신호를 받으면 on_signal 함수를 실행합니다."""

    def listen():
        while True:
            try:
                connection, _ = server_socket.accept()
                connection.close()
                on_signal()
            except OSError:
                break
            except Exception:
                break

    listener_thread = threading.Thread(target=listen, daemon=True)
    listener_thread.start()


# =========================
# 북스타트 계산 로직
# =========================

def clean_birth_text(raw_text):
    """생년월일 입력값에서 공백과 구분 기호를 제거합니다."""

    return (
        raw_text
        .replace(" ", "")
        .replace("-", "")
        .replace(".", "")
        .replace("/", "")
    )


def guess_year_from_short_birth(yy, today):
    """6자리 생년월일의 앞 두 자리로 출생연도를 추정합니다."""

    current_year_short = today.year % 100

    if yy > current_year_short + 1:
        return 1900 + yy

    return 2000 + yy


def parse_birthdate(raw_text, today):
    """입력된 생년월일을 date 객체로 변환합니다."""

    birth = clean_birth_text(raw_text)

    if not birth.isdigit() or len(birth) not in (6, 8):
        raise ValueError("형식 오류\n예: 241023 또는 20241023")

    if len(birth) == 6:
        yy = int(birth[:2])
        year = guess_year_from_short_birth(yy, today)
        month = int(birth[2:4])
        day = int(birth[4:6])
    else:
        year = int(birth[:4])
        month = int(birth[4:6])
        day = int(birth[6:8])

    try:
        return date(year, month, day)
    except ValueError:
        raise ValueError("날짜 입력 오류\n월/일을 확인하세요")


def calculate_months_old(birth_date, today):
    """생년월일 기준으로 현재까지 지난 개월 수를 계산합니다."""

    months_old = (today.year - birth_date.year) * 12 + today.month - birth_date.month

    if today.day < birth_date.day:
        months_old -= 1

    return months_old


def get_stage_message(birth_date, months_old, today):
    """개월 수와 출생연도를 기준으로 북스타트 단계를 판정합니다."""

    if months_old < 0:
        return "미래에서 오셨나요?\n아직 태어나지 않았어요!", COLOR_ERROR

    if months_old >= 228:
        return f"{months_old}개월 / 어르신...?!\n생년월일을 다시 확인하세요", COLOR_WARNING

    if birth_date.year <= today.year - 7:
        return f"{months_old}개월 / 초등학생 이상\n학교를 간 아가는 아가가 아니다!", COLOR_ERROR

    if months_old <= 18:
        return f"{months_old}개월 / 수령 가능!\n1단계", COLOR_SUCCESS

    if months_old <= 35:
        return f"{months_old}개월 / 수령 가능!\n2단계", COLOR_SUCCESS

    return f"{months_old}개월 / 수령 가능!\n3단계", COLOR_SUCCESS


# =========================
# 화면 구성
# =========================

class BookStartApp:
    def __init__(self, root, server_socket):
        self.root = root
        self.server_socket = server_socket
        self.entry = None
        self.result_label = None

        self.configure_window()
        self.apply_icon()
        self.create_widgets()
        self.bind_events()
        self.start_single_instance_listener()

    def configure_window(self):
        self.root.title(APP_NAME)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*WINDOW_MIN_SIZE)
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def apply_icon(self):
        try:
            self.root.iconbitmap(resource_path(ICON_FILE))
        except Exception:
            pass

    def create_widgets(self):
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(side="bottom", fill="x", pady=(2, 6))

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.create_header(main_frame)
        self.create_input(main_frame)
        self.create_buttons(main_frame)
        self.create_result_label(main_frame)
        self.create_footer(footer_frame)

    def create_header(self, parent):
        title_label = tk.Label(parent, text="생년월일 입력", font=FONT_TITLE)
        title_label.pack(pady=(16, 2))

        guide_label = tk.Label(
            parent,
            text="예: 241023 또는 20241023",
            font=FONT_GUIDE,
            fg=COLOR_GUIDE,
        )
        guide_label.pack()

    def create_input(self, parent):
        self.entry = tk.Entry(parent, width=16, justify="center", font=FONT_INPUT)
        self.entry.pack(pady=(10, 8))
        self.entry.focus_set()

    def create_buttons(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=(0, 8))

        check_button = tk.Button(
            button_frame,
            text="계산",
            width=8,
            font=FONT_BUTTON,
            command=self.check_stage,
        )
        check_button.pack(side="left", padx=4)

        clear_button = tk.Button(
            button_frame,
            text="초기화",
            width=8,
            font=FONT_BUTTON,
            command=self.clear_input,
        )
        clear_button.pack(side="left", padx=4)

    def create_result_label(self, parent):
        self.result_label = tk.Label(
            parent,
            text="날짜를 입력해주세요",
            font=FONT_RESULT,
            wraplength=280,
            fg=COLOR_NORMAL,
        )
        self.result_label.pack(pady=(2, 5))

    def create_footer(self, parent):
        footer_app_label = tk.Label(
            parent,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=FONT_FOOTER,
            fg=COLOR_FOOTER,
        )
        footer_app_label.pack()

        footer_developer_label = tk.Label(
            parent,
            text=f"Developed by {DEVELOPER_NAME}",
            font=FONT_FOOTER,
            fg=COLOR_FOOTER,
        )
        footer_developer_label.pack()

    def bind_events(self):
        self.root.bind("<Return>", self.check_stage)

    def start_single_instance_listener(self):
        start_instance_listener(
            self.server_socket,
            lambda: self.root.after(0, self.bring_window_to_front),
        )

    def bring_window_to_front(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.focus_set()

    def check_stage(self, event=None):
        today = date.today()

        try:
            birth_date = parse_birthdate(self.entry.get(), today)
        except ValueError as error:
            self.result_label.config(text=str(error), fg=COLOR_ERROR)
            return

        months_old = calculate_months_old(birth_date, today)
        message, color = get_stage_message(birth_date, months_old, today)
        self.result_label.config(text=message, fg=color)

    def clear_input(self):
        self.entry.delete(0, tk.END)
        self.result_label.config(text="날짜를 입력해주세요", fg=COLOR_NORMAL)
        self.entry.focus_set()

    def close(self):
        try:
            self.server_socket.close()
        except Exception:
            pass

        self.root.destroy()


# =========================
# 프로그램 시작점
# =========================

def main():
    server_socket = acquire_single_instance()

    root = tk.Tk()
    app = BookStartApp(root, server_socket)
    root.mainloop()


if __name__ == "__main__":
    main()
