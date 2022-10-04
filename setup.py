from cx_Freeze import setup, Executable

base = "Win32GUI"

exes = [Executable(script="PyCurrentWindow.py",
                   base=base,
                   target_name="PyCurrentWindow.exe",
                   icon="images/icon.ico")]

opts = {'build_exe': {'build_exe': 'executable',
                      'include_files': ['src/', 'LICENSE', 'images/'],
                      'includes': ['win32process'],
                      'excludes': ["tkinter"]}}

setup(options=opts,
      name="PyCurrentWindow",
      version="1.0",
      description="PyCurrentWindow",
      author="David Blum",
      license="MIT",
      packages=['src'],
      executables=exes)
