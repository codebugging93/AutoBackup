from gui.Home_Layout import root 

# UI 요소와 버튼 클릭 요소는 분리하여 진행함 
# Home_Layout 파일을 components.py로 바꾸고
# 각 컴포넌트에 바인딩된 기능들을 functions.py에 몰아넣음
# main.py에서는 from gui.functions import init을 호출하여 
# mainloop를 수행하게 함 

# functions.py
# 1. 폴더 선택창의 값을 AppData에 적용하는 것부터 시작
# 2. 검사 모드를 Appdata에 넣음
# 3. 검사를 시작함
"""
    system/system_values.py에 클래스를 하나 만들어서 
    진행중인 시스템 함수의 변수를 클래스에 실시간으로 집어넣고,
    
    gui/realtime_widgets.py 파일을 만들고
    gui의 값을 1초에 30번 갱신할 수 있도록
    system_values의 값을 1초에 30번씩 불러와서 update 시킨다.   
    * tick 변수를 두어 어떤 변수는 1초에 5번만 바뀌도록 속도 조절을 시킨다.
    이렇게 업데이트 하는 코드는 while True로 감싼 뒤에
    하나의 함수로 만들어 놓는다.
    
    realtime_widgets에서 만든 함수를 Thread를 사용하여 
    gui/functions.py에서 init할때 병렬 처리 시킨다.
"""

# 4. 검사 결과를 Appdata에 저장하고, 각 리스트박스에 표시함
# 아까의 로직을 재활용하여 백업, 재검사, 최적화 진행도 표시함 
# 모든 작업이 끝나면 백업 결과를 표시하고 처음 화면으로 돌아감


UI팀 이승민씨는 일단 UI 파일이 동작할 수 있게 완성해주시고, 
그 뒤에 components.py와 functions.py로 분리해주시는것을 부탁드립니다.

SYS팀 박상현씨는 compare, backup, aftercheck의 각 함수에서 발생하는 값을 
UI에 표시할 수 있도록, AppData와 비슷한 클래스인 SystemValues를 만들어서 
저장할 수 있도록 합니다.


root.mainloop()

