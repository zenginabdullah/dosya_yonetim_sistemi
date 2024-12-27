import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
from tkinter import ttk
from user_dashboard import *
from admin_dashboard import *
from tkinter import Label, Frame
from PIL import Image, ImageTk
from logger import log_action
import user

db_path = "app.db"

def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')

def login(db_path, username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        db_password, role = result
        if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
            return True, role
        else:
            return False, None
    else:
        return False, None

def handle_register():
    register_window = tk.Toplevel()
    register_window.title("Kayıt Ol")
    register_window.geometry("350x450")
    register_window.resizable(False, False)
    register_window.configure(bg="#f2f2f2")
    center_window(register_window, 350, 450)
    
    register_resim = Image.open("photos/register.png")
    register_resim = register_resim.resize((100, 100))
    register_resim = ImageTk.PhotoImage(register_resim)
    rresim = Label(register_window,image=register_resim)
    rresim.place(x=10,y=10)
    rresim.image = register_resim
    rresim.pack(pady=10)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12), background="#f2f2f2")
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=5)

    register_frame = ttk.LabelFrame(register_window, text="Kullanıcı Kaydı", padding=(10, 10))
    register_frame.pack(padx=20, pady=10, fill="both", expand=False)
    
    ttk.Label(register_frame, text="Kullanıcı Adı:").pack(pady=10)
    entry_new_username = ttk.Entry(register_frame, width=30)
    entry_new_username.pack(pady=5)

    ttk.Label(register_frame, text="Parola:").pack(pady=10)
    entry_new_password = ttk.Entry(register_frame, show="*", width=30)
    entry_new_password.pack(pady=5)

    def submit_registration():
        username = entry_new_username.get()
        password = entry_new_password.get()
        if not username or not password:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return
        register_user(username, password, register_window)

    ttk.Button(register_window, text="Kayıt Ol", command=submit_registration).pack(pady=20)

def register_user(username, password, register_window):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, "user"))
        conn.commit()
        
        user_id = user.User.get_user_id(username)
        messagebox.showinfo("Başarılı", "Kayıt başarıyla tamamlandı!")
        log_action(user_id, "Kullanıcı Kaydı", f"{username} adlı kullanıcı kayıt oldu.")
        
        register_window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

def handle_login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")
        return

    success, role = login(db_path, username, password)
    if success:
        messagebox.showinfo("Giriş Başarılı", f"Hoş geldiniz, {username}!")
        user_id = user.User.get_user_id(username)
        log_action(user_id, "Kullanıcı Girişi", f"{username} adlı kullanıcı giriş yaptı.")
        
        root.withdraw()
        if role == "user":
            open_user_dashboard(username)
        elif role == "admin":
            open_admin_dashboard(username)
    else:
        messagebox.showerror("Giriş Başarısız", "Kullanıcı adı veya parola hatalı.")

def create_login_window():
    global entry_username, entry_password, root

    root = tk.Tk()
    root.title("Kullanıcı Girişi")
    root.geometry("350x450")
    root.resizable(False, False)
    root.configure(bg="#f2f2f2")
    center_window(root, 350, 450)
    
    login_resim = Image.open("photos/login.png")
    login_resim = login_resim.resize((100, 100))
    login_resim = ImageTk.PhotoImage(login_resim)
    lresim = Label(root,image=login_resim)
    lresim.place(x=10,y=10)
    lresim.image = login_resim
    lresim.pack(pady=10)
    
    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12), background="#f2f2f2")
    style.configure("TEntry", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12), padding=5)
    
    login_frame = ttk.LabelFrame(root, text="Kullanıcı Girişi", padding=(10, 10))
    login_frame.pack(padx=20, pady=10, fill="both", expand=False)
    
    ttk.Label(login_frame, text="Kullanıcı Adı:").pack(pady=10)
    entry_username = ttk.Entry(login_frame, width=30)
    entry_username.pack(pady=5)

    ttk.Label(login_frame, text="Parola:").pack(pady=10)
    entry_password = ttk.Entry(login_frame, show="*", width=30)
    entry_password.pack(pady=5)

    ttk.Button(root, text="Giriş Yap", command=handle_login).pack(pady=5)
    ttk.Button(root, text="Kayıt Ol", command=handle_register).pack(pady=5)

    root.mainloop()

create_login_window()
