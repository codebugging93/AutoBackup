"""
진행 화면(윗줄/아랫줄 진행률)을 주기적으로 갱신한다.

검사/백업/복사마다 따로 있던 갱신 함수를 하나(UiUpdater.update)로 합쳤다.
진행 화면은 두 줄로 되어 있고, 줄마다 메시지/값/최대값/경로를 SystemValues에 따로 적는다.

    윗줄  : top_progress_msg,    top_progress_val,    top_progress_max,    top_progress_path
    아랫줄: bottom_progress_msg, bottom_progress_val, bottom_progress_max, bottom_progress_path

아랫줄은 bottom_progress_visible이 True일 때만 보인다. (False이면 한 줄짜리 진행 화면)
경과 시간은 progress_start_time부터 잰다.

- 스레드는 QThread를 쓰고, 정지 신호는 QThread에 내장된
  requestInterruption()/isInterruptionRequested()를 사용한다(Qt가 보장하는 스레드 안전 API).
- 위젯 갱신은 call_in_gui_thread로 GUI 스레드에 넘겨서 실행하므로,
  위젯 접근은 항상 GUI 스레드에서만 일어난다.
"""

import time

from PySide6.QtCore import QThread

import gui.components as widgets
from system.path import PREFIX_MAX_PATH
from system.SystemValues import SystemValues

_TICK_INTERVAL_MS = 1000 // 60  # 60Hz


class _UpdateThread(QThread):
    """
    1/60초마다 UiUpdater.update를 GUI 스레드에서 실행되도록 예약하는 워커 스레드.

    처음엔 tick 시그널을 만들어서 밖에서 Qt.QueuedConnection으로 연결하는 방식으로 짰었는데,
    UiUpdater.start()가 (run_compare 등의) 백그라운드 스레드에서 호출될 때는
    그 connect() 자체가 GUI 스레드가 아닌 그 백그라운드 스레드 기준으로 걸려버려서,
    거기엔 이벤트 루프가 없으니 큐에 쌓이기만 하고 실제로는 절대 실행되지 않는 문제가 있었다
    (진행바가 안 움직이던 원인). 그래서 어느 스레드에서 start()를 부르든 항상 안전하게
    GUI 스레드로 넘겨주는 call_in_gui_thread를 직접 쓰도록 바꿈.
    """

    def run(self):
        while not self.isInterruptionRequested():
            widgets.call_in_gui_thread(UiUpdater.update)
            self.msleep(_TICK_INTERVAL_MS)
        widgets.call_in_gui_thread(UiUpdater.update)  # 종료 시 한번 더 업데이트


class UiUpdater:
    _thread: "_UpdateThread | None" = None

    @classmethod
    def start(cls):
        cls.stop()  # 혹시 이전 스레드가 아직 살아있다면 먼저 정리

        thread = _UpdateThread()
        cls._thread = thread
        thread.start()

    @classmethod
    def stop(cls):
        thread = cls._thread
        if thread is None:
            return
        cls._thread = None
        thread.requestInterruption()
        thread.wait()  # 스레드가 실제로 종료될 때까지 대기

    @classmethod
    def update(cls):
        # ---------- 윗줄 ----------
        # 프로그레스바
        max_value = SystemValues.top_progress_max
        current_value = SystemValues.top_progress_val
        widgets.top_progressbar.setMaximum(max(max_value, 1))  # 0이면 busy 애니메이션 되는 것 방지
        widgets.top_progressbar.setValue(min(current_value, max(max_value, 1)))

        # 진행률 표시
        percentage = _get_percentage(current_value, max_value)
        message = SystemValues.top_progress_msg
        widgets.label_top_progress.setText(f"{message} {current_value}/{max_value} ({percentage:.1f}%)")

        # 문자열 표시 (경로 등)
        widgets.label_top_progress3.setText(summarize_str(SystemValues.top_progress_path))

        # 경과 시간 (윗줄 오른쪽)
        time_str = _get_time_str(time.time() - SystemValues.progress_start_time)
        widgets.label_top_progress2.setText(time_str)

        # ---------- 아랫줄: 필요할 때만 보인다 ----------
        if not SystemValues.bottom_progress_visible:
            widgets.frame_bottom_progress.hide()
            return

        widgets.frame_bottom_progress.show()

        # 프로그레스바
        max_value = SystemValues.bottom_progress_max
        current_value = SystemValues.bottom_progress_val
        widgets.bottom_progressbar.setMaximum(max(max_value, 1))
        widgets.bottom_progressbar.setValue(min(current_value, max(max_value, 1)))

        # 진행률 표시
        percentage = _get_percentage(current_value, max_value)
        message = SystemValues.bottom_progress_msg
        widgets.label_bottom_progress.setText(f"{message} {current_value}/{max_value} ({percentage:.1f}%)")

        # 문자열 표시 (경로 등)
        widgets.label_bottom_progress3.setText(summarize_str(SystemValues.bottom_progress_path))


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
