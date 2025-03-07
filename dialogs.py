"""Functions about dialogs."""

import tkinter
import tkinter.filedialog
import tkinter.messagebox


def open_files() -> tuple[str, str] | None:
    """Open two files to analyze."""
    if files := tkinter.filedialog.askopenfilenames(initialdir="./examples"):
        if len(files) == 2:
            return files[:2]
        tkinter.messagebox.showerror("错误", f"应该选择两个文件进行分析\n而不是 {len(files)} 个文件！")
    return None
