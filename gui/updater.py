"""
gui/updater.py(tkinter)를 PySide6로 번역한 버전입니다.

기존 tkinter 버전을 그대로 옮기지 않고, PySide6에 맞게 QThread 기반으로 다시 짰습니다.
- 원본은 threading.Thread + 폴링용 bool 플래그(running)로 스레드를 제어했는데,
  Qt 앱에서는 QThread를 쓰는 것이 정석이라 QThread로 교체했습니다.
- 정지 신호는 직접 만든 bool 플래그 대신 QThread에 내장된
  requestInterruption()/isInterruptionRequested()를 사용합니다(Qt가 보장하는 스레드 안전 API).
- 실제 위젯 갱신은 QThread 쪽에서 emit한 시그널을 Qt.QueuedConnection으로 받아
  GUI 스레드의 이벤트 루프에서 실행되므로, 위젯 접근이 항상 GUI 스레드에서만 일어남을 보장합니다.
"""

import time

from PySide6.QtCore import QThread

import gui.components as widgets
from system.path import PREFIX_MAX_PATH
from system.SystemValues import SystemValues

_TICK_INTERVAL_MS = 1000 // 60  # 60Hz


class _UpdateThread(QThread):
    """
    1/30초마다 func를 GUI 스레드에서 실행되도록 예약하는 워커 스레드.

    처음엔 tick 시그널을 만들어서 밖에서 Qt.QueuedConnection으로 연결하는 방식으로 짰었는데,
    UiUpdater.start()가 (run_compare 등의) 백그라운드 스레드에서 호출될 때는
    그 connect() 자체가 GUI 스레드가 아닌 그 백그라운드 스레드 기준으로 걸려버려서,
    거기엔 이벤트 루프가 없으니 큐에 쌓이기만 하고 실제로는 절대 실행되지 않는 문제가 있었다
    (진행바가 안 움직이던 원인). 그래서 어느 스레드에서 start()를 부르든 항상 안전하게
    GUI 스레드로 넘겨주는 components_pyside6.call_in_gui_thread를 직접 쓰도록 바꿈.
    """

    def __init__(self, func):
        super().__init__()
        self._func = func

    def run(self):
        while not self.isInterruptionRequested():
            widgets.call_in_gui_thread(self._func)
            self.msleep(_TICK_INTERVAL_MS)
        widgets.call_in_gui_thread(self._func)  # 종료 시 한번 더 업데이트


class UiUpdater:
    _thread: "_UpdateThread | None" = None

    @classmethod
    def start(cls, func):
        cls.stop()  # 혹시 이전 스레드가 아직 살아있다면 먼저 정리

        thread = _UpdateThread(func)
        cls._thread = thread
        thread.start()

    @classmethod
    def stop(cls):
        thread = cls._thread
        if thread is None:
            return
        cls._thread = None
        thread.requestInterruption()
        thread.wait()  # 스레드가 실제로 종료될 때까지 대기 (tkinter판의 "sleep(0.5) 후 기대"와 달리 확정적으로 종료를 보장)

    @classmethod
    def update_compare(cls):
        # 프로그레스바
        max_value = SystemValues.compare_progress_max
        current_value = SystemValues.compare_progress_val
        widgets.top_progressbar.setMaximum(max(max_value, 1))  # 0이면 busy 애니메이션 되는 것 방지
        widgets.top_progressbar.setValue(min(current_value, max(max_value, 1)))

        # 진행률 표시
        percentage = _get_percentage(current_value, max_value)
        string = f"파일 검사 중 {current_value}/{max_value} ({percentage:.1f}%)"
        widgets.label_top_progress.setText(string)

        # 경로 표시
        path = summarize_str(SystemValues.compare_progress_path)
        widgets.label_top_progress3.setText(path)

        # 시간 표시
        time_str = _get_time_str(time.time() - SystemValues.compare_start_time)
        widgets.label_top_progress2.setText(time_str)

    @classmethod
    def update_backup(cls):
        # 프로그레스바
        max_value = SystemValues.backup_progress_max
        current_value = SystemValues.backup_progress_val
        widgets.top_progressbar.setMaximum(max(max_value, 1))
        widgets.top_progressbar.setValue(min(current_value, max(max_value, 1)))

        # 진행률 표시
        percentage = _get_percentage(current_value, max_value)
        message = SystemValues.backup_progress_msg
        string = f"{message} {current_value}/{max_value} ({percentage:.1f}%)"
        widgets.label_top_progress.setText(string)

        # 경로 표시
        path = summarize_str(SystemValues.backup_progress_path)
        widgets.label_top_progress3.setText(path)

        # 시간 표시
        time_str = _get_time_str(time.time() - SystemValues.backup_start_time)
        widgets.label_top_progress2.setText(time_str)

        if SystemValues.copy_working:
            widgets.frame_bottom_progress.show()
        else:
            widgets.frame_bottom_progress.hide()

        # 프로그레스바
        bottom_max = SystemValues.copy_progress_max
        bottom_value = SystemValues.copy_progress_val
        widgets.bottom_progressbar.setMaximum(max(bottom_max, 1))
        widgets.bottom_progressbar.setValue(min(bottom_value, max(bottom_max, 1)))

        # 진행률 표시
        percentage = _get_percentage(bottom_value, bottom_max)
        string = f"파일 복사 중 {bottom_value}/{bottom_max} ({percentage:.1f}%)"
        widgets.label_bottom_progress.setText(string)

        # 경로 표시
        path = summarize_str(SystemValues.copy_progress_path)
        widgets.label_bottom_progress3.setText(path)


def _get_percentage(current_value, max_value):
    if max_value == 0:
        percentage = 0
    else:
        percentage = int((current_value / max_value * 100) * 10) / 10
    return percentage


def _get_time_str(time_delta):
    total_sec = int(time_delta)
    total_min = total_sec // 60
    total_hour = total_min // 60
    seconds = total_sec % 60
    minutes = total_min % 60
    hours = total_hour
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_str


def summarize_str(p):
    p = p.removeprefix(PREFIX_MAX_PATH)
    return p if len(p) <= 70 else p[:35] + "..." + p[-35:]
