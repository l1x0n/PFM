from tkinter import *
from tkinter import messagebox as msbox
from tkinter import ttk
from datetime import datetime
import os
import shutil
import pathlib
import ctypes

app_icon = "assets/PFM-icon.ico"
current_path = os.getcwd()
clipboard = []
is_cut = False


# УТИЛИТЫ
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")

def size_unit(size):
    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if size < 1024:
            return f"{round(size, 2):g} {unit}"
        size /= 1024

def is_hidden(path):
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    if (attrs & 2) and not view_show_hidden.get():
        return True
    return False

def calc_drive():
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    drives = []
    for i in range(26):
        if bitmask & (1 << i):
            drives.append(chr(65 + i) + ":\\")
    return drives


# ЛОГИКА
def load_directory(path):
    tree.delete(*tree.get_children())
    path_var.set(path)
    drive_var.set(path[0:3])

    try:
        items = os.listdir(path)
        items.sort(key=lambda x:(
            not os.path.isdir(os.path.join(path, x)),
            x.lower()
        ))

        for item in items:
            full_path = os.path.join(path, item)

            if is_hidden(full_path):
                continue

            time = os.path.getmtime(full_path)
            time = datetime.fromtimestamp(time).strftime("%d.%m.%Y %H:%M")

            if os.path.isdir(full_path):
                size = ""
                file_type = "Папка"
            else:
                size = os.path.getsize(full_path)
                size = size_unit(size)
                file_type = "Файл"
        
            tree.insert("", "end", values=(item, time, file_type, size))
    except PermissionError:
        msbox.showerror("Ошибка", "Отказано в доступе")
        backward()
    except Exception as e:
        msbox.showerror("Ошибка", f"Не удалось прочитать: {e}")

def open_item(event):
    global current_path

    selected = tree.selection()
    if not selected:
        return
    
    item = tree.item(selected[0])
    name = item["values"][0]
    path = os.path.join(current_path, name)

    if os.path.isdir(path):
        current_path = path
        load_directory(current_path)
    else:
        os.startfile(path)

def delete_item(event=None):
    global current_path

    selected = tree.selection()
    if not selected:
        return
    
    for i in selected: 
        name = tree.item(i)["values"][0]
        path = os.path.join(current_path, name)

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError as e:
            msbox.showerror("Ошибка удаления", e)
        
    load_directory(current_path)

def copy(event=None):
    global current_path
    global clipboard
    global is_cut

    clipboard = []
    is_cut = False

    selected = tree.selection()
    if not selected:
        return
    
    for i in selected: 
        name = tree.item(i)["values"][0]
        path = os.path.join(current_path, name)
        clipboard.append(path)

def paste(event=None):
    global current_path
    global clipboard
    global is_cut

    for i in clipboard:
        goal = os.path.join(current_path, os.path.basename(i))

        if is_cut:
            shutil.move(i, goal)
        else:
            if os.path.exists(goal):
                if os.path.isdir(goal):
                    shutil.rmtree(goal)
                else:
                    os.remove(goal)

            if os.path.isdir(i):
                shutil.copytree(i, goal)
            else:
                shutil.copy2(i, goal)
    if is_cut:
        clipboard = []
        is_cut = False

    load_directory(current_path)

def cut(event=None):
    global is_cut
    copy()
    is_cut = True

def backward():
    global current_path
    current_path = str(pathlib.Path(current_path).parent)
    load_directory(current_path)

def change_drive(path):
    global current_path
    current_path = path
    load_directory(path)
    show_drive_frame()

def entry_path_load(event):
    global current_path
    path = path_var.get()
    if os.path.exists(path):
        current_path = path
        load_directory(current_path)


# ОКНА
def create_file_dialog():
    global current_path

    create_file_window = Toplevel(root)
    create_file_window.title("Создание файла")
    center_window(create_file_window, 300, 80)
    create_file_window.iconbitmap(app_icon)

    entry = Entry(create_file_window)
    entry.pack(fill="x", padx=5, expand=True, side="top")
    entry.focus_set()

    def create_file():
        name = entry.get()
        if name:
            path = os.path.join(current_path, name)
            with open(path, "w") as f:
                pass
            load_directory(current_path)
            create_file_window.destroy()

    control_frame = Frame(create_file_window)
    control_frame.pack(fill="x", side="bottom")

    Button(control_frame, text="Отмена", command=create_file_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Создать", command=create_file).pack(side="right", padx=5, pady=5)

def create_dir_dialog():
    global current_path

    create_dir_window = Toplevel(root)
    create_dir_window.title("Создание папки")
    center_window(create_dir_window, 300, 80)
    create_dir_window.iconbitmap(app_icon)

    entry = Entry(create_dir_window)
    entry.pack(fill="x", padx=5, expand=True, side="top")
    entry.focus_set()

    def create_dir():
        name = entry.get()
        if name:
            path = os.path.join(current_path, name)
            os.mkdir(path)
            load_directory(current_path)
            create_dir_window.destroy()

    control_frame = Frame(create_dir_window)
    control_frame.pack(fill="x", side="bottom")

    Button(control_frame, text="Отмена", command=create_dir_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Создать", command=create_dir).pack(side="right", padx=5, pady=5)


# УПРАВЛЕНИЕ ИНТЕРФЕЙСОМ
def show_drive_frame():
    global drive_frame

    if drive_frame is not None:
        drive_frame.destroy()
        drive_frame = None
        return 
    
    drive_frame = Frame(root, bg="white", relief="ridge", borderwidth=2)
    drive_frame.place(x=34, y=33)

    drive_frame.focus_set()
    drive_frame.bind("<FocusOut>", lambda e: show_drive_frame())

    drives = calc_drive()
    for d in drives:
        btn = Button(drive_frame, text=d, anchor="w", width=2, relief="groove", 
            command=lambda path=d: change_drive(path))
        btn.pack(fill="x")


# ЗАГЛУШКА
def not_implemented():
    msbox.showinfo("PFM", "Эта функция пока не реализована")


ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
root.title("PFM")
center_window(root, 700, 500)
root.iconbitmap(app_icon)


# верхнее меню 
top_menu = Menu(root)

# файл
file_menu = Menu(top_menu, tearoff=0)
file_create_menu = Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Создать", menu=file_create_menu)
file_create_menu.add_command(label="Файл", command=create_file_dialog)
file_create_menu.add_command(label="Папку", command=create_dir_dialog)
file_menu.add_command(label="Свойства", accelerator="Alt+Enter", command=not_implemented)

file_menu.add_separator()
file_menu.add_command(label="Параметры", command=not_implemented)
file_menu.add_command(label="Выход", accelerator="Alt+F4", command=root.quit)

# правка
edit_menu = Menu(top_menu, tearoff=0)
edit_menu.add_command(label="Копировать", accelerator="Ctrl+C", command=copy)
edit_menu.add_command(label="Вырезать", accelerator="Ctrl+X", command=cut)
edit_menu.add_command(label="Вставить", accelerator="Ctrl+V", command=paste)

edit_menu.add_separator()
edit_menu.add_command(label="Удалить", accelerator="Del", command=delete_item)

# вид
view_menu = Menu(top_menu, tearoff=0)
view_mode_menu = Menu(view_menu, tearoff=0)
view_mode_var = StringVar(value="Таблица")
view_mode_menu.add_radiobutton(label="Сетка", variable=view_mode_var)
view_mode_menu.add_radiobutton(label="Список", variable=view_mode_var)
view_mode_menu.add_radiobutton(label="Таблица", variable=view_mode_var)

view_sort_menu = Menu(view_menu, tearoff=0)
view_sort_var = StringVar(value="По дате")
view_sort_menu.add_radiobutton(label="По имени", variable=view_sort_var)
view_sort_menu.add_radiobutton(label="По размеру", variable=view_sort_var)
view_sort_menu.add_radiobutton(label="По дате", variable=view_sort_var)
view_menu.add_cascade(label="Сортировка", menu=view_sort_menu)

view_menu.add_separator()
view_show_hidden = BooleanVar()
view_menu.add_checkbutton(label="Скрытые файлы", variable=view_show_hidden, command=lambda: load_directory(current_path))

# сборка верхнего меню
top_menu.add_cascade(label="Файл", menu=file_menu)
top_menu.add_cascade(label="Правка", menu=edit_menu)
top_menu.add_cascade(label="Вид", menu=view_menu)
root.config(menu=top_menu)


# навигация
nav_frame = Frame(root, relief="flat", bg="white", bd=0)
nav_frame.pack(fill="x")

back_button = Button(nav_frame, text="↑", width=2, height=1, command=backward)
back_button.pack(side="left", padx=5, pady=5)

drive_var = StringVar(value=current_path[0]+":\\")
change_button = Button(nav_frame, textvariable=drive_var, width=2, command=show_drive_frame)
change_button.pack(side="left", padx=[2, 3], pady=5)

drive_frame = None

path_var = StringVar(value=current_path)
path_entry = Entry(nav_frame, textvariable=path_var)
path_entry.pack(side="left", fill="x", expand=True, padx=5)

# древо файлов
tree_frame = Frame(root)
tree_frame.pack(fill="both", expand=True)

columns = ("name", "time", "type", "size")

tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.heading("name", text="Имя")
tree.heading("time", text="Дата изменения")
tree.heading("type", text="Тип")
tree.heading("size", text="Размер")
tree.column("name", width=250, minwidth=150, anchor="w")
tree.column("time", width=150, minwidth=100, anchor="center")
tree.column("type", width=100, minwidth=80, anchor="center")
tree.column("size", width=100, minwidth=80, anchor="e")
tree.pack(fill="both", expand=True)


#бинды
root.bind("<Control-c>", copy)
root.bind("<Control-x>", cut)
root.bind("<Control-v>", paste)
root.bind("<F5>", lambda e: load_directory(current_path))
path_entry.bind("<Return>", entry_path_load)
tree.bind("<Double-1>", open_item)
tree.bind("<Delete>", delete_item)


load_directory(current_path)
root.mainloop()