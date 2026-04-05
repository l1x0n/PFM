from tkinter import *
from tkinter import messagebox as msbox
from tkinter import ttk
from tkinter import font
from datetime import datetime
import os
import shutil
import pathlib
import ctypes
import locale

app_icon = "assets/PFM-icon.ico"
current_path = os.getcwd()
clipboard = []
is_cut = False
locale.setlocale(locale.LC_TIME, 'rus_rus')

# УТИЛИТЫ
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")

def set_icon(win):
    if os.path.exists(app_icon):
        win.iconbitmap(app_icon)
    else:
        pass

def size_unit(size):
    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ"]:
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

def calc_dir_size(path):
    size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            filepath = os.path.join(dirpath, f)
            if os.path.exists(filepath):
                size += os.path.getsize(filepath)
    return size


# ЛОГИКА
def sort_items(path, items, mode, asc):
    rev = (asc == "По убыванию")

    if mode == "По имени":
            items.sort(key=lambda x: x.lower(), reverse=not rev)
            items.sort(key=lambda x: not os.path.isdir(os.path.join(path, x)))
    elif mode == "По дате":
            items.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=rev)
            items.sort(key=lambda x: not os.path.isdir(os.path.join(path, x)))
    elif mode == "По размеру":
            items.sort(key=lambda x: os.path.getsize(os.path.join(path, x)), reverse=rev)
            items.sort(key=lambda x: not os.path.isdir(os.path.join(path, x)))

    return items

def load_directory(path):
    tree.delete(*tree.get_children())
    path_var.set(path)
    drive_var.set(path[0:3])

    try:
        items = os.listdir(path)
        items = sort_items(path, items, view_sort_var.get(), view_order_var.get())

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

def open_item(event=None):
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
            if os.path.abspath(i) == os.path.abspath(goal):
                continue
            elif os.path.exists(goal):
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
    set_icon(create_file_window)
    create_file_window.transient(root)
    create_file_window.grab_set()

    entry = Entry(create_file_window)
    entry.pack(fill="x", padx=5, expand=True, side="top")
    entry.focus_set()

    def create_file(event=None):
        name = entry.get()
        if name:
            path = os.path.join(current_path, name)
            with open(path, "w") as f:
                pass
            load_directory(current_path)
            create_file_window.destroy()

    create_file_window.bind("<Return>", create_file)

    control_frame = Frame(create_file_window)
    control_frame.pack(fill="x", side="bottom")

    Button(control_frame, text="Отмена", command=create_file_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Создать", command=create_file).pack(side="right", padx=5, pady=5)

def create_dir_dialog():
    global current_path

    create_dir_window = Toplevel(root)
    create_dir_window.title("Создание папки")
    center_window(create_dir_window, 300, 80)
    set_icon(create_dir_window)
    create_dir_window.transient(root)
    create_dir_window.grab_set()

    entry = Entry(create_dir_window)
    entry.pack(fill="x", padx=5, expand=True, side="top")
    entry.focus_set()

    def create_dir(event=None):
        name = entry.get()
        if name:
            path = os.path.join(current_path, name)
            os.mkdir(path)
            load_directory(current_path)
            create_dir_window.destroy()

    create_dir_window.bind("<Return>", create_dir)

    control_frame = Frame(create_dir_window)
    control_frame.pack(fill="x", side="bottom")

    Button(control_frame, text="Отмена", command=create_dir_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Создать", command=create_dir).pack(side="right", padx=5, pady=5)

def rename_dialog(event=None):
    global current_path

    selected = tree.selection()
    if not selected:
        return
        
    item = tree.item(selected[0])
    name = item["values"][0]
    path = os.path.join(current_path, name)
    name, ext = os.path.splitext(name)

    rename_window = Toplevel(root)
    rename_window.title("Переименовывание")
    center_window(rename_window, 300, 80)
    set_icon(rename_window)
    rename_window.transient(root)
    rename_window.grab_set()

    entry = Entry(rename_window)
    entry.insert(0, name + ext)
    entry.selection_range(0, len(name))
    entry.icursor(len(name))
    entry.pack(fill="x", padx=5, expand=True, side="top")
    entry.focus_set()

    error_label = ttk.Label(rename_window, text="", foreground="red")
    error_label.pack(padx=5, pady=0, side="top", anchor="w")

    def rename_item(event=None):
        new_name = os.path.join(current_path, entry.get())
        error_label.config(text="")
        
        if not entry.get():
            error_label.config(text="Имя не может быть пустым")
            entry.focus_set()
            return
        if os.path.exists(new_name) and entry.get() != name + ext:
            error_label.config(text="Файл с таким именем уже существует")
            entry.focus_set()
            return
        try:
            if entry.get() != name + ext:
                shutil.move(path, new_name)
            load_directory(current_path)
            rename_window.destroy()
        except Exception as e:
            error_label.config(text=f"Ошибка: {e}")
            entry.focus_set()

    rename_window.bind("<Return>", rename_item)
    
    control_frame = Frame(rename_window)
    control_frame.pack(fill="x", side="bottom")

    Button(control_frame, text="Отмена", command=rename_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Переименовать", command=rename_item).pack(side="right", padx=5, pady=5)

def properties(event=None):
    selected = tree.selection()
    if not selected:
        return
    
    item = tree.item(selected[0])
    name = item["values"][0]
    path = os.path.join(current_path, name)

    location = os.path.dirname(path)
    ctime = os.path.getctime(path)
    ctime = datetime.fromtimestamp(ctime).strftime("%A, %d.%m.%Y %H:%M:%S")
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    readonly = 1 if (attrs & 1) else 0
    hidden = 1 if (attrs & 2) else 0

    if os.path.isdir(path):
        file_type = "Папка"
        size = size_unit(calc_dir_size(path))
    else:
        file_type = "Файл"                                              
        size = size_unit(os.path.getsize(path))
        mtime = os.path.getmtime(path)
        mtime = datetime.fromtimestamp(mtime).strftime("%A, %d.%m.%Y %H:%M:%S")
        atime = os.path.getatime(path)
        atime = datetime.fromtimestamp(atime).strftime("%A, %d.%m.%Y %H:%M:%S")


    prop_window = Toplevel(root)
    prop_window.title("Свойства")
    center_window(prop_window, 400, 450)
    set_icon(prop_window)
    prop_window.focus_set()

    entry = Entry(prop_window)
    entry.pack(fill="x", padx=10, pady=[30, 5], side="top")
    entry.insert(0, name)

    error_label = ttk.Label(prop_window, text="", foreground="red")
    error_label.pack(padx=10, pady=0, side="top", anchor="w")

    ttk.Separator(prop_window, orient="horizontal").pack(fill="x", padx=10, pady=5, side="top")
    ttk.Label(prop_window, text=f"Тип: {file_type}").pack(padx=10, pady=5, side="top", anchor="w")
    ttk.Label(prop_window, text=f"Расположение: {location}").pack(padx=10, pady=5, side="top", anchor="w")
    ttk.Label(prop_window, text=f"Размер: {size}").pack(padx=10, pady=5, side="top", anchor="w")

    ttk.Separator(prop_window, orient="horizontal").pack(fill="x", padx=10, pady=5, side="top")
    ttk.Label(prop_window, text=f"Создан: {ctime}").pack(padx=10, pady=5, side="top", anchor="w")
    if not os.path.isdir(path):
        ttk.Label(prop_window, text=f"Изменен: {mtime}").pack(padx=10, pady=5, side="top", anchor="w")
        ttk.Label(prop_window, text=f"Открыт: {atime}").pack(padx=10, pady=5, side="top", anchor="w")

    ttk.Separator(prop_window, orient="horizontal").pack(fill="x", padx=10, pady=5, side="top")
    attrs_frame = Frame(prop_window)
    attrs_frame.pack(fill="x", side="top")
    ttk.Label(attrs_frame, text="Атрибуты:").pack(padx=10, pady=5, side="left")
    var_readonly = IntVar()
    var_readonly.set(readonly)
    var_hidden = IntVar()
    var_hidden.set(hidden)
    cb_readonly = Checkbutton(attrs_frame, text="Только чтение", variable=var_readonly)
    cb_hidden = Checkbutton(attrs_frame, text="Скрытый", variable=var_hidden)
    cb_readonly.pack(padx=10, pady=5, side="left")
    cb_hidden.pack(padx=10, pady=5, side="left")

    def prop_apply():
        new_name = os.path.join(location, entry.get())
        error_label.config(text="")

        if not entry.get():
            error_label.config(text="Имя не может быть пустым")
            entry.focus_set()
            return
        if os.path.exists(new_name) and entry.get() != name:
            error_label.config(text="Файл с таким именем уже существует")
            entry.focus_set()
            return
        try:
            if entry.get() != name:
                shutil.move(path, new_name)
        except Exception as e:
            error_label.config(text=f"Ошибка: {e}")
            entry.focus_set()
        
        attrs = ctypes.windll.kernel32.GetFileAttributesW(new_name)
        
        if var_readonly.get():
            attrs |= 1
        else:
            attrs &= ~1
        if var_hidden.get():
            attrs |= 2
        else:
            attrs &= ~2
        ctypes.windll.kernel32.SetFileAttributesW(new_name, attrs)

        load_directory(current_path)
        prop_window.destroy()

    control_frame = Frame(prop_window)
    control_frame.pack(fill="x", side="bottom")
    Button(control_frame, text="Отмена", command=prop_window.destroy).pack(side="right", padx=5, pady=5)
    Button(control_frame, text="Применить", command=prop_apply).pack(side="right", padx=5, pady=5)


# УПРАВЛЕНИЕ ИНТЕРФЕЙСОМ
def show_drive_frame():
    global drive_frame

    if drive_frame is not None:
        drive_frame.destroy()
        drive_frame = None
        return 
    
    drive_frame = Frame(root, bg="white", relief="ridge", borderwidth=2)
    drive_frame.place(x=35, y=33)

    drive_frame.focus_set()
    drive_frame.bind("<FocusOut>", lambda e: show_drive_frame())

    drives = calc_drive()
    for d in drives:
        btn = Button(drive_frame, text=d, font=("Sans-Serif", 10), anchor="w", width=2, relief="groove", 
            command=lambda path=d: change_drive(path))
        btn.pack(fill="x")

def show_context_menu(event):
    context_menu.delete(0, "end")
    item = tree.identify_row(event.y)
    if item:
        tree.selection_set(item)   
        tree.focus(item)
        context_menu.add_command(label="Открыть", command=open_item)
        context_menu.add_separator()
        context_menu.add_command(label="Копировать", command=copy)
        context_menu.add_command(label="Вырезать", command=cut)
        context_menu.add_separator()
        context_menu.add_command(label="Переименовать", command=rename_dialog)
        context_menu.add_command(label="Удалить", command=delete_item)
    else:
        tree.selection_remove(tree.selection())
        if clipboard:
            context_menu.add_command(label="Вставить", command=paste)
            context_menu.add_separator()
        context_sort_menu = Menu(context_menu, tearoff=0)
        context_sort_menu.add_radiobutton(label="По имени", variable=view_sort_var, command=lambda: load_directory(current_path))
        context_sort_menu.add_radiobutton(label="По дате", variable=view_sort_var, command=lambda: load_directory(current_path))
        context_sort_menu.add_radiobutton(label="По размеру", variable=view_sort_var, command=lambda: load_directory(current_path))

        context_sort_menu.add_separator()
        context_sort_menu.add_radiobutton(label="По возрастанию", variable=view_order_var, command=lambda: load_directory(current_path))
        context_sort_menu.add_radiobutton(label="По убыванию", variable=view_order_var, command=lambda: load_directory(current_path))
        context_menu.add_cascade(label="Сортировка", menu=context_sort_menu)
        context_menu.add_separator()
        context_create_menu = Menu(context_menu, tearoff=0)
        context_create_menu.add_command(label="Файл", command=create_file_dialog)
        context_create_menu.add_command(label="Папку", command=create_dir_dialog)
        context_menu.add_cascade(label="Создать", menu=context_create_menu)
    if item:
        context_menu.add_separator()
        context_menu.add_command(label="Свойства", command=properties)

    context_menu.tk_popup(event.x_root, event.y_root)
    context_menu.grab_release()

# ЗАГЛУШКА
def not_implemented():
    msbox.showinfo("PFM", "Эта функция пока не реализована")


# КОНФИГУРАЦИЯ И СТИЛИ
ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
root.title("PFM")
center_window(root, 700, 500)
set_icon(root)
default_font = font.nametofont("TkDefaultFont")
default_font.config(family="Segoe UI", size=10)
root.option_add("*Font", default_font)


# ГЛАВНОЕ МЕНЮ
top_menu = Menu(root)

# файл
file_menu = Menu(top_menu, tearoff=0)
file_create_menu = Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Создать", menu=file_create_menu)
file_create_menu.add_command(label="Файл", command=create_file_dialog)
file_create_menu.add_command(label="Папку", command=create_dir_dialog)
file_menu.add_command(label="Свойства", accelerator="Alt+Enter", command=properties)

file_menu.add_separator()
file_menu.add_command(label="Выход", accelerator="Alt+F4", command=root.quit)

# правка
edit_menu = Menu(top_menu, tearoff=0)
edit_menu.add_command(label="Копировать", accelerator="Ctrl+C", command=copy)
edit_menu.add_command(label="Вырезать", accelerator="Ctrl+X", command=cut)
edit_menu.add_command(label="Вставить", accelerator="Ctrl+V", command=paste)

edit_menu.add_separator()
edit_menu.add_command(label="Переименовать", accelerator="F2", command=rename_dialog)
edit_menu.add_command(label="Удалить", accelerator="Del", command=delete_item)

# вид
view_menu = Menu(top_menu, tearoff=0)

view_sort_menu = Menu(view_menu, tearoff=0)
view_sort_var = StringVar(value="По имени")
view_sort_menu.add_radiobutton(label="По имени", variable=view_sort_var, command=lambda: load_directory(current_path))
view_sort_menu.add_radiobutton(label="По дате", variable=view_sort_var, command=lambda: load_directory(current_path))
view_sort_menu.add_radiobutton(label="По размеру", variable=view_sort_var, command=lambda: load_directory(current_path))

view_sort_menu.add_separator()
view_order_var = StringVar(value="По убыванию")
view_sort_menu.add_radiobutton(label="По возрастанию", variable=view_order_var, command=lambda: load_directory(current_path))
view_sort_menu.add_radiobutton(label="По убыванию", variable=view_order_var, command=lambda: load_directory(current_path))
view_menu.add_cascade(label="Сортировка", menu=view_sort_menu)

view_menu.add_separator()
view_show_hidden = BooleanVar()
view_menu.add_checkbutton(label="Скрытые файлы", variable=view_show_hidden, command=lambda: load_directory(current_path))

# сборка верхнего меню
top_menu.add_cascade(label="Файл", menu=file_menu)
top_menu.add_cascade(label="Правка", menu=edit_menu)
top_menu.add_cascade(label="Вид", menu=view_menu)
root.config(menu=top_menu)


# ПАНЕЛЬ НАВИГАЦИИ
nav_frame = Frame(root, relief="flat", bg="white", bd=0)
nav_frame.pack(fill="x")

back_button = Button(nav_frame, text="↑", font=("Sans-Serif", 10), width=2, height=1, command=backward)
back_button.pack(side="left", padx=[5,3], pady=5)

drive_var = StringVar(value=current_path[0]+":\\")
change_button = Button(nav_frame, textvariable=drive_var, font=("Sans-Serif", 10), width=2, command=show_drive_frame)
change_button.pack(side="left", padx=[3,5], pady=5)
drive_frame = None

path_var = StringVar(value=current_path)
path_entry = Entry(nav_frame, textvariable=path_var)
path_entry.pack(side="left", fill="x", expand=True, padx=5)


# ДРЕВО ФАЙЛОВ
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


# ГОРЯЧИЕ КЛАВИШИ И СОБЫТИЯ
context_menu = Menu(root, tearoff=0)

root.bind("<Control-c>", copy)
root.bind("<Control-x>", cut)
root.bind("<Control-v>", paste)
root.bind("<F5>", lambda e: load_directory(current_path))
tree.bind("<Button-3>", show_context_menu)
tree.bind("<Double-1>", open_item)
tree.bind("<Delete>", delete_item)
tree.bind("<F2>", rename_dialog)
tree.bind("<Alt-Return>", properties)
path_entry.bind("<Return>", entry_path_load)


# ЗАПУСК
load_directory(current_path)
root.mainloop()