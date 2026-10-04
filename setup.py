from cx_Freeze import Executable, setup
from system.constants import APPNAME, VERSION


executables = [Executable(
    "main.py", 
    base="gui", 
    icon="image/logo.ico",
    target_name=APPNAME,
    )]

build_exe_options = {
    "include_files": ["image"],
}


setup(
    name=APPNAME,
    version=VERSION,
    description=APPNAME,
    options={"build_exe": build_exe_options},
    executables=executables,
)