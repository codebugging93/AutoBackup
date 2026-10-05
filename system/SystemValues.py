class SystemValues:
    # 진행 화면(gui/updater.py)이 읽는 값
    # 윗줄
    top_progress_msg = ""
    top_progress_val = 0
    top_progress_max = 0
    top_progress_path = ""
    # 아랫줄 (bottom_progress_visible이 True일 때만 보임)
    bottom_progress_msg = ""
    bottom_progress_val = 0
    bottom_progress_max = 0
    bottom_progress_path = ""
    bottom_progress_visible = False
    # 경과 시간의 기준
    progress_start_time = 0.0

    optimized_count = 0 


    