import tkinter as tk


__all__ = [
    "VerticalScrollbar",
    "LabelListboxWithFrame",
]



class EntryWithFrame:
    """ 
    엔트리의 속성을 변경하려면 self.entry를 사용 할 것\n
    프레임의 속성은 웬만하면 변경하면 안 되나, self.frame 사용
    """
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.entry = tk.Entry(self.frame)


    def bind_cmd(self, cmd, key="<Return>"):
        """
        대답을 받고 cmd를 실행한다.
        """
        self.entry.bind(key, lambda event=None: cmd())


    def write(self, string):
        """
        엔트리에 string을 삽입하려면 state == "normal"이어야 하므로
        삽입이 끝나면 원래의 state로 되돌린다.
        """
        _org_state = self.entry["state"]
        self.entry["state"] = "normal"
        self.entry.delete(0, "end")
        self.entry.insert("end", string)
        self.entry["state"] = _org_state

    
    def clear(self):
        _org_state = self.entry["state"]
        self.entry["state"] = "normal"
        self.entry.delete(0, "end")
        # self.entry.insert("end", string)
        self.entry["state"] = _org_state

    
    def reset(self):
        self.clear()
        self.bind_cmd(lambda: None)

    
    def pack_custom(self, **kwargs):
        """
        kwargs는 프레임을 배치하는 데 쓰이고,
        프레임 내부에 entry가 padx=10의 갭만 가진 상태로
        프레임 내부를 꽉 채우도록 되어있다.
        """
        self.frame.pack(**kwargs)
        self.entry.pack(fill="both", expand=True, padx=5)


class CustomText(tk.Text):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)


    def print(self, *vars, sep=" ", end="\n"):
        self["state"] = "normal"
        string = sep.join(vars) + end
        self.insert('end', string)
        self.see('end')
        self["state"] = "disabled"


    def clear(self):
        self["state"] = "normal"
        self.delete("1.0", "end")
        self["state"] = "disabled"


class VerticalScrollbar(tk.Scrollbar):
    """ 세로 스크롤바 """
    def __init__(self, frame, widget):
        super().__init__(
            frame,
            command=widget.yview,
            orient="vertical"
            )

        widget.config(yscrollcommand=self.set)


class LabelListboxWithFrame:
    """ 추천 변수명: llbox_... """
    def __init__(self, master, message):
        self.frame = tk.Frame(master)
        self.listbox = tk.Listbox(self.frame)
        self.label = tk.Label(self.frame, text=message)
        self.scrollbar = VerticalScrollbar(self.frame, self.listbox)
        self.MESSAGE = message
 

    def add(self, string):
        self.listbox.insert("end", string)


    def clear(self):
        self.listbox.delete(0, "end")
        self.label.config(text=self.MESSAGE)
    

    def indicate_num(self):
        string = f"{self.MESSAGE} ({self.listbox.size()})"
        self.label.config(text=string)

    
    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)
        self.label.pack(fill='x')
        self.scrollbar.pack(side='right', fill='y')
        self.show_listbox()


    def hide_listbox(self):
        """ 리스트박스를 업데이트할때 속도를 높이기 위해서 사용함 """
        self.listbox.pack_forget()

    
    def show_listbox(self):
        self.listbox.pack(side='left', fill='both', expand=True)

