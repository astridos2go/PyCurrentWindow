from cx_Freeze import Executable, setup

base = "Win32GUI"

exes = [
    Executable(
        script="PyCurrentWindow.py",
        base=base,
        target_name="PyCurrentWindow.exe",
        icon="pycurrentwindow/images/icon.ico",
    )
]

opts = {
    "build_exe": {
        "build_exe": "executable",
        "include_files": ["pycurrentwindow/", "LICENSE", "pycurrentwindow/images"],
        "includes": ["win32process"],
        "excludes": ["tkinter"],
    }
}

setup(
    options=opts,
    name="PyCurrentWindow",
    version="1.1",
    description="PyCurrentWindow",
    author="David Blum",
    license="MIT",
    executables=exes,
)
