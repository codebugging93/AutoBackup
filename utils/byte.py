_byte_strings = ("바이트", "KB", "MB", "GB", "TB")


def convert_byte(byte) -> tuple[str, str]:
    """
    바이트를 나눠서 세자리로 만든 byte_str과,
    바이트를 괄호에 담은 detail을 반환한다.
    """
    
    original_byte = byte
    
    # 바이트 계산
    exponential = 0
    while byte >= 1000 and exponential < 4:
        byte /= 1024
        exponential += 1

    # 소수 정리
    byte_str = _cut_decimal_3(byte)
    
    # 접미사 
    suffix = _byte_strings[exponential]
    byte_str += suffix

    # 괄호 속 바이트
    if exponential == 0:
        detail = ""
    else:
        detail = f"({original_byte:,}{_byte_strings[0]})"
    
    return byte_str, detail


# 소수 자름
def _cut_decimal_3(byte: int | float) -> str: 
    """ 
    정수부의 자릿수가 3자리 이하여야 하고, 4자리 부터는 소수부를 없앤다. 
    byte에는 e가 있어선 안 된다.
    """
    string = str(float(byte)) # float는 무료로 점을 드립니다
    integer, decimal = string.split(".")

    # integer의 자릿수와 decimal의 자릿수의 합이 3이 되도록 함
    decimal_length = 3 - len(integer) 
    if decimal_length <= 0: # 아니라면 정수만 반환
        return integer
    
    # 너무 큰 수
    if string.find("e") != -1:
        raise Exception("too large value for calculating byte")
    
    decimal += "0" # 9.0 같은 수에 decimal_length만큼 맞추는 과정 
    decimal = decimal[:decimal_length]  # 길이에 맞게 자름
    byte_str = f"{integer}.{decimal}"
    return byte_str



