import tkinter
import tkinter.filedialog
import tkinter.ttk

import maliang
import maliang.theme

import dialogs
import highlight
import process


def get_files() -> tuple[str, str] | None:
    """Get files"""
    if files := dialogs.open_files():
        files = tuple(reversed(files))
        with open(files[0], "r", encoding="utf-8") as file:
            old.delete("0.0", "end")
            old_file = file.read()
        with open(files[1], "r", encoding="utf-8") as file:
            new.delete("0.0", "end")
            new_file = file.read()
        print("OPEN FILES:")
        print(f"old_file: {files[0]}")
        print(f"new_file: {files[1]}")
        return old_file, new_file
    return None


def apply_files() -> None:
    """Apply files opened to the `tkinter.Text` widget."""
    if files := get_files():
        old.insert("0.0", files[0])
        new.insert("0.0", files[1])
        process_files(files)


def add_tags(widget: tkinter.Text, data: dict[tuple[int, int], str], row: int) -> None:
    """Add tags to strings."""
    for cols, tag in data.items():
        widget.tag_add(tag, f"{row}.{cols[0]}", f"{row}.{cols[1]}")


# def process_files(files: tuple[str, str]) -> None:
#     """Process files."""
#     for i, lines in enumerate(zip(files[0].split(), files[1].split())):
#         ops = process.get_diff(lines[0], lines[1])
#         add_tags(old, ops[0], i + 1)
#         add_tags(new, ops[1], i + 1)


def process_files(files: tuple[str, str]) -> None:
    """Process files."""
    ops = process.get_diff(*files)
    for cols, tag in ops[0].items():
        old.tag_add(tag, old.index(f"1.0 + {cols[0]} chars"), old.index(f"1.0 + {cols[1]} chars"))
    for cols, tag in ops[1].items():
        new.tag_add(tag, new.index(f"1.0 + {cols[0]} chars"), new.index(f"1.0 + {cols[1]} chars"))


maliang.theme.set_color_mode("light")

tk = maliang.Tk(title="Block Diff")
tk.center()
tk.alpha(0.90)

cv = maliang.Canvas(tk, width=1280, height=720, auto_zoom=True)
cv.place(width=1280, height=720)

menu = tkinter.Menu(tk)
tk.configure(menu=menu)

file_menu = tkinter.Menu(menu, tearoff=False)
file_menu.add_command(label="打开(O)", command=apply_files, accelerator="Ctrl+O")
file_menu.add_command(label="保存(S)", command=lambda: print("保存"), accelerator="Ctrl+S")

option_menu = tkinter.Menu(menu, tearoff=False)

help_menu = tkinter.Menu(menu, tearoff=False)

menu.add_cascade(menu=file_menu, label="文件(F)")
menu.add_cascade(menu=option_menu, label="选项(O)")
menu.add_cascade(menu=help_menu, label="帮助(H)")

old = tkinter.Text(cv, font=("Consolas", 12), wrap="none")
new = tkinter.Text(cv, font=("Consolas", 12), wrap="none")
old.place(x=0, y=0, width=640, height=720)
new.place(x=640, y=0, width=640, height=720)

highlight.register_color_tags(old, new)

# old.configure(selectforeground="", selectbackground="blue")

bar_old_v = tkinter.ttk.Scrollbar(old, orient="vertical", command=old.yview, cursor="arrow")
bar_old_v.pack(side="right", fill="y")
bar_new_v = tkinter.ttk.Scrollbar(new, orient="vertical", command=new.yview, cursor="arrow")
bar_new_v.pack(side="right", fill="y")
bar_old_h = tkinter.ttk.Scrollbar(old, orient="horizontal", command=old.xview, cursor="arrow")
bar_old_h.pack(side="bottom", fill="x")
bar_new_h = tkinter.ttk.Scrollbar(new, orient="horizontal", command=new.xview, cursor="arrow")
bar_new_h.pack(side="bottom", fill="x")

old.configure(xscrollcommand=bar_old_h.set, yscrollcommand=bar_old_v.set)
new.configure(xscrollcommand=bar_new_h.set, yscrollcommand=bar_new_v.set)

tk.mainloop()
