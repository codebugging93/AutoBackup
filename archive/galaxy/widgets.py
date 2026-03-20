import tkinter as tk 
from TKgui.custom_widgets import EntryWithFrame, CustomText, VerticalScrollbar

__all__ = [
    "root",
    "label_progress_main",
    "label_progress_sub",
    "entry_ans_with_frame",
    "frame_log",
    "text_log",
    "scroll_log",
    "btn_start",
]

root = tk.Tk()
label_progress_main = tk.Label(root)
label_progress_sub = tk.Label(root)
entry_ans_with_frame = EntryWithFrame(root)
        
frame_log = tk.Frame(root)
text_log = CustomText(frame_log)
scroll_log = VerticalScrollbar(frame_log, text_log)

btn_start = tk.Button(root)
       


