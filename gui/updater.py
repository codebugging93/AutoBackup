from threading import Thread
import time

from system.SystemValues import SystemValues
import gui.components as widgets

summarize_str = lambda p: p if len(p) <= 70 else p[:35] + "..." + p[-35:]

class UiUpdater:
    running = False 
    
    @classmethod
    def update_loop(cls, func):
        """
        1초에 30번 UI를 갱신하는 메인 루프입니다.
        이 함수는 GUI의 메인 스레드를 방해하지 않도록 별도의 Thread에서 실행되어야 합니다.
        """
        cls.running = True 
        tick = 0
        while cls.running:
            tick = (tick + 1) % 30  # 30Hz 주기로 tick 순환 (0~29)

            func(tick)

            time.sleep(1 / 30)      # 약 0.033초 대기

        func(tick) # 종료시 한번 더 업데이트

    @classmethod
    def start(cls, func):
        Thread(target=cls.update_loop, args=(func, )).start()


    @classmethod
    def stop(cls):
        cls.running = False


    @classmethod 
    def update_compare(cls, tick):
        # 프로그레스바 
        widgets.top_progressbar.config(
            value=SystemValues.compare_progress_val, 
            maximum=SystemValues.compare_progress_max
            )

        # 진행률 표시 
        current_value = SystemValues.compare_progress_val
        max_value = SystemValues.compare_progress_max
        percentage = _get_percentage(current_value, max_value)
        string = f"파일 검사 중 {current_value}/{max_value} ({percentage:.1f}%)"
        widgets.label_top_progress.config(text=string)
        
        # 경로 표시
        path = summarize_str(SystemValues.compare_progress_path)
        widgets.label_top_progress3.config(text=path)

        # 시간 표시
        time_str = _get_time_str(time.time() - SystemValues.compare_start_time)
        widgets.label_top_progress2.config(text=time_str)


    @classmethod 
    def update_backup(cls, tick):
        # 프로그레스바 
        widgets.top_progressbar.config(
            value=SystemValues.backup_progress_val, 
            maximum=SystemValues.backup_progress_max
            )

        # 진행률 표시 
        current_value = SystemValues.backup_progress_val
        max_value = SystemValues.backup_progress_max
        percentage = _get_percentage(current_value, max_value)
        message = SystemValues.backup_progress_msg
        string = f"{message} {current_value}/{max_value} ({percentage:.1f}%)"
        widgets.label_top_progress.config(text=string)
        
        # 경로 표시
        path = summarize_str(SystemValues.compare_progress_path)
        widgets.label_top_progress3.config(text=path)

        # 시간 표시
        time_str = _get_time_str(time.time() - SystemValues.backup_start_time)
        widgets.label_top_progress2.config(text=time_str)


        if SystemValues.copy_working:
            widgets.frame_bottom_progress.pack(fill='x')
        else:
            widgets.frame_bottom_progress.pack_forget()

        # 프로그레스바 
        widgets.bottom_progressbar.config(
            value=SystemValues.copy_progress_val, 
            maximum=SystemValues.copy_progress_max
            )

        # 진행률 표시 
        current_value = SystemValues.copy_progress_val
        max_value = SystemValues.copy_progress_max
        percentage = _get_percentage(current_value, max_value)
        string = f"파일 복사 중 {current_value}/{max_value} ({percentage:.1f}%)"
        widgets.label_bottom_progress.config(text=string)
        
        # 경로 표시
        path = summarize_str(SystemValues.compare_progress_path)
        widgets.label_bottom_progress3.config(text=path)

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
