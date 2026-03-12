from tkinter import *
from tkinter import messagebox as msbox
from tkinter import ttk
import os
import ctypes
import pathlib


ctypes.windll.shcore.SetProcessDpiAwareness(True)

def not_implemented():
    msbox.showinfo("PFM", "Эта функция пока не реализована")


root = Tk()
root.title("PFM")
root.geometry("700x500")

top_menu = Menu(root)

# файл
file_menu = Menu(top_menu, tearoff=0)
file_menu.add_command(label="Новое окно", accelerator="Ctrl+N", command=not_implemented)
file_create_menu = Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Создать", menu=file_create_menu)
file_create_menu.add_command(label="Файл", command=not_implemented)
file_create_menu.add_command(label="Папку", command=not_implemented)
file_menu.add_command(label="Свойства", accelerator="Alt+Enter", command=not_implemented)

file_menu.add_separator()
file_menu.add_command(label="Параметры", command=not_implemented)
file_menu.add_command(label="Выход", accelerator="Alt+F4", command=root.quit)

# правка
edit_menu = Menu(top_menu, tearoff=0)
edit_menu.add_command(label="Копировать", accelerator="Ctrl+C", command=not_implemented)
edit_menu.add_command(label="Вырезать", accelerator="Ctrl+X", command=not_implemented)
edit_menu.add_command(label="Вставить", accelerator="Ctrl+V", command=not_implemented)

edit_menu.add_separator()
edit_menu.add_command(label="Удалить", accelerator="Del", command=not_implemented)

# вид
view_menu = Menu(top_menu, tearoff=0)
view_mode_menu = Menu(view_menu, tearoff=0)
view_mode_var = StringVar(value="Таблица")
view_mode_menu.add_radiobutton(label="Сетка", variable=view_mode_var)
view_mode_menu.add_radiobutton(label="Список", variable=view_mode_var)
view_mode_menu.add_radiobutton(label="Таблица", variable=view_mode_var)
view_menu.add_cascade(label="Режим иконок", menu=view_mode_menu)

view_sort_menu = Menu(view_menu, tearoff=0)
view_sort_var = StringVar(value="По дате")
view_sort_menu.add_radiobutton(label="По имени", variable=view_sort_var)
view_sort_menu.add_radiobutton(label="По размеру", variable=view_sort_var)
view_sort_menu.add_radiobutton(label="По дате", variable=view_sort_var)
view_menu.add_cascade(label="Сортировка", menu=view_sort_menu)

view_menu.add_separator()
view_show_hidden = BooleanVar()
view_menu.add_checkbutton(label="Скрытые файлы", variable=view_show_hidden)

# сборка верхнего меню
top_menu.add_cascade(label="Файл", menu=file_menu)
top_menu.add_cascade(label="Правка", menu=edit_menu)
top_menu.add_cascade(label="Вид", menu=view_menu)

root.config(menu=top_menu)

# просмотр фалов 
container = Frame(root)
container.pack(fill="both", expand=True)

columns = ("name", "size", "type")

tree = ttk.Treeview(container, columns=columns, show="headings")
tree.heading("name", text="Имя")
tree.heading("size", text="Размер")
tree.heading("type", text="Тип")
tree.pack(fill="both", expand=True)

#бинды
root.bind("<Control-n>", lambda e: not_implemented())
root.bind("<Alt-Return>", lambda e: not_implemented())
root.bind("<Control-c>", lambda e: not_implemented())
root.bind("<Control-x>", lambda e: not_implemented())
root.bind("<Control-v>", lambda e: not_implemented())
root.bind("<Delete>", lambda e: not_implemented())

root.mainloop()