from threading import Thread
from time import time, sleep

from system.byte import convert_byte



class TypeIncorrectError(Exception):
    def __init__(self, varname, _type):
        self.msg = f"variable {varname} must be {str(_type)}"


    def __str__(self):
        return self.msg
    

class Progress:
    """
    처음에는 .update를 해도 아무런 기능을 하지 않는다.
    .bind_writing으로 기능을 지정해주어야 한다.
    """
    def __init__(self):
        self.prefix = ""
        self.num = 0
        self.total = 0

        self.fps = 60
        self.is_visible = True # 업데이트와는 무관하게 표시를 할 것인지 여부를 따짐
        self.isupdate = False # 이게 참이여야 업데이트가 됨
        self.thread = None # 스레드 보관용 변수
        self.cmd = lambda: None # update_base에서 작동시킬 함수

        self.write: function # 다른 곳에서 할당할 함수
        self.clear: function


    def bind_writing(self, function_to_write, function_to_clear):
        self.write = function_to_write
        self.clear = function_to_clear


    def update_progress(self):
        self.cmd = self._ud_progress
        self._update()

    def update_count(self):
        self.cmd = self._ud_count
        self._update()

    def update_byte(self): 
        self.cmd = self._ud_byte
        self._update()

    def update_wait(self):
        self.cmd = self._ud_wait
        self._update()

    def stop(self):
        """
        메인 스레드에서 사용 금지;
        버튼 클릭 커맨드에서 이걸 쓰면 모든 스레드가 멈춰버림
        self.update_base를 중단시키고, self의 스레드를 중단시킨다.
        """
        self.isupdate = False
        self.thread.join()


    def on(self):
        self.is_visible = True


    def off(self):
        self.is_visible = False


    def reset(self, prefix="", num=0, total=0):
        """ 초기화와 동시에 선언 가능 """
        self.config(prefix=prefix, num=num, total=total)


    def config(self, prefix=None, num=None, total=None):
        """ 특정 값만 변경 가능 """

        if isinstance(prefix, str):
            self.prefix = prefix
        elif prefix is not None:  # str도 none도 아니면
            raise TypeIncorrectError("prefix", str)

        if isinstance(num, int):
            self.num = num
        elif num is not None:
            raise TypeIncorrectError("num", int)

        if isinstance(total, int):
            self.total = total
        elif total is not None:
            raise TypeIncorrectError("total", int)
        

    def _update(self):
        self.isupdate = True
        self.thread = Thread(target=self._update_base)
        self.thread.start() # 스레드 시작


    def _update_base(self):
        waiting = ""
        fpsdt = 1 / self.fps
        tick1 = time()
        tick2 = time()
        while self.isupdate:
            # on일때 표시
            if self.is_visible:
                # 점, 틱 계산
                loss = time() - tick2
                if loss < 0.2:
                    waiting = "┏"
                elif loss < 0.4:
                    waiting = "┓"
                elif loss < 0.6:
                    waiting = "┛"
                elif loss < 0.8:
                    waiting = "┗"
                else:
                    tick2 = time()

                # 텍스트 출력
                string = self.cmd()
                string += "    " + waiting
                self.write(string)

            # off일때 표시 X 
            elif not self.is_visible:
                self.clear()

            # 프레임 처리
            dt = time() - tick1
            if dt < fpsdt:
                sleep(fpsdt - dt)
            tick1 = time()


        # 99%로 보이는것 방지
        if self.is_visible:
            string = self.cmd()
            self.write(string)
        elif not self.is_visible:
            self.clear()


    # 진행률을 표시하는 로딩바
    def _ud_progress(self):
        prefix = self.prefix
        num = self.num
        total = self.total

        # 퍼센트 계산
        try:
            percentage = num / total * 100
            percentage = int(percentage * 10) / 10
        except ZeroDivisionError:
            percentage = 100.0

        # 문자열 생성
        string = f"{prefix} {percentage}%  ({num}/{total})"

        return string


    # 개수를 세는 로딩바
    def _ud_count(self):
        prefix = self.prefix
        num = self.num
        string = f"{prefix} {num}개"

        return string


    # 바이트를 세는 로딩바
    def _ud_byte(self):
        prefix = self.prefix
        num = self.num

        byte_str, detail = convert_byte(num)
        string = f"{prefix} {byte_str} {detail}"

        return string


    # 작업 대기
    def _ud_wait(self):
        return self.prefix


