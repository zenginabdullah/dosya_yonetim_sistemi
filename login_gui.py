import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
from tkinter import ttk
from user_dashboard import *
from admin_dashboard import *
from tkinter import Label
from PIL import Image, ImageTk
from logger import log_action
import user
import datetime
from collections import defaultdict
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_sync import BackupAndSyncHandler
import time
from tkinter.ttk import Progressbar


def start_file_sync():
    source_dir = "source"  # İzlenecek kaynak dizin
    dest_dir = "backup"  # Yedekleme dizini
    os.makedirs(dest_dir, exist_ok=True)

    # Toplam dosya sayısını hesapla
    total_files = len([f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))])
    if total_files == 0:
        print("Yedeklenecek dosya bulunamadı.")
        return

    # GUI penceresi oluştur
    sync_window = tk.Tk()
    sync_window.title("Yedekleme ve Senkronizasyon")
    sync_window.geometry("300x150")
    sync_window.configure(bg="#f2f2f2")

    tk.Label(sync_window, text="Yedekleme işlemi devam ediyor...", bg="#f2f2f2").pack(pady=10)
    progress = Progressbar(sync_window, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress.pack(pady=20)

    def on_sync_complete():
        tk.Label(sync_window, text="Yedekleme tamamlandı!", bg="#f2f2f2", fg="green").pack(pady=10)
        sync_window.after(2000, sync_window.destroy)  # Pencereyi 2 saniye sonra kapatır

    # BackupAndSyncHandler'ı başlat
    event_handler = BackupAndSyncHandler(progress, total_files, on_sync_complete)
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=False)

    def start_observer():
        observer.start()
        print("Yedekleme ve senkronizasyon başlatıldı...")

        for file in os.listdir(source_dir):
            file_path = os.path.join(source_dir, file)
            if os.path.isfile(file_path):
                event_handler.backup_file(file_path)

        observer.stop()
        observer.join()

    # İşlem arka planda çalıştırılır
    threading.Thread(target=start_observer, daemon=True).start()

    def stop_observer():
        observer.stop()
        observer.join()
        sync_window.destroy()

    sync_window.protocol("WM_DELETE_WINDOW", stop_observer) # Pencere kapatıldığında gözlemciyi durdur
    
    sync_window.mainloop()

# Yedekleme thread'ini başlat
sync_thread = threading.Thread(target=start_file_sync, daemon=True)
sync_thread.start()


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
        
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]
        
        check_failed_login(user_id)

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
    
FAILED_LOGIN_THRESHOLD = 3
LOCK_TIME = datetime.timedelta(minutes=10)

failed_logins = defaultdict(list)
    
def check_failed_login(user_id):
    """Başarısız giriş denemeleri tespit edilir."""
    current_time = datetime.datetime.now()
    
    failed_logins[user_id] = [t for t in failed_logins[user_id] if current_time - t < LOCK_TIME]

    if len(failed_logins[user_id]) >= FAILED_LOGIN_THRESHOLD:
        send_alert(user_id)

        log_anomalous_behavior(user_id, "Cok fazla giris denemesi.")

    failed_logins[user_id].append(current_time)

def send_alert(user_id):
    messagebox.showerror("Uyarı", "Kısa süre içerisinde çok fazla yanlış giriş denemesinde bulundunuz.")

def log_anomalous_behavior(user_id, behavior):
    """Anormal davranışı log dosyasına kaydeder."""
    with open("anomalous_behavior.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {user_id} - {behavior}\n")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO anomalies (user_id, type, detected_at, details) VALUES(?,?,?,?)",(user_id, "Fazla Giriş Denemesi", datetime.datetime.now(), f"{user_id} id'li kullanıcı çok fazla yanlış giriş denemesinde bulundu."))
    conn.commit()
        
create_login_window()
