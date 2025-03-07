import tkinter
import tkinter.filedialog
import tkinter.ttk

import maliang
import maliang.theme

import dialogs
import highlight


def apply_files() -> None:
    """Apply files opened to the `tkinter.Text` widget."""
    if files := dialogs.open_files():
        with open(files[0], "r", encoding="utf-8") as file:
            old.delete("0.0", "end")
            old.insert("0.0", file.read())
        with open(files[1], "r", encoding="utf-8") as file:
            new.delete("0.0", "end")
            new.insert("0.0", file.read())


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

old = tkinter.Text(cv, font=("Consolas", 12))
new = tkinter.Text(cv, font=("Consolas", 12))
# old.pack(side="left")
# new.pack(side="right")
# old.grid(row=0, column=0)
# new.grid(row=0, column=1)
old.place(x=0, y=0, width=640, height=720)
new.place(x=640, y=0, width=640, height=720)

highlight.register_color_tags(old, new)

# old.configure(selectforeground="", selectbackground="blue")

bar_old = tkinter.ttk.Scrollbar(old, orient="vertical", command=old.yview, cursor="arrow")
bar_old.pack(side="right", fill="y")
bar_new = tkinter.ttk.Scrollbar(new, orient="vertical", command=new.yview, cursor="arrow")
bar_new.pack(side="right", fill="y")

old.configure(yscrollcommand=bar_old.set)
new.configure(yscrollcommand=bar_new.set)

# old.insert("1.0", "Hello, World!\n")
# old.insert("2.0", "Hello, World!\n")
# old.insert("3.0", "Hello, World!\n")
# old.insert("4.0", "Hello, World!\n")
# old.insert("5.0", "Hello, World!\n")
# old.insert("6.0", "Hello, World!\n")
# old.insert("7.0", "Hello, World!\n")

# old.tag_add("insert", "1.0", "1.end")
# old.tag_add("delete", "2.0", "2.end")
# old.tag_add("update", "3.0", "3.end")
# old.tag_add("copy", "4.0", "4.end")
# old.tag_add("move", "5.0", "5.end")
# old.tag_add("merge", "6.0", "6.end")
# old.tag_add("split", "7.0", "7.end")

tk.mainloop()
