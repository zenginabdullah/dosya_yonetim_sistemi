import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import admin as a
import user

def open_admin_dashboard(username):
    admin_dashboard = tk.Toplevel()
    admin_dashboard.title(f"Admin Paneli: {username}")
    admin_dashboard.geometry("500x350")
    admin_dashboard.configure(bg="#f2f2f2")
    center_window(admin_dashboard, 500, 350)

    ttk.Label(admin_dashboard, text="Admin Paneli", font=("Arial", 18, "bold"), background="#f2f2f2").pack(pady=20)

    def approve_password_change(username):
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_change_requested = 2 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Onay", f"{username} kullanıcısının parola değiştirme talebi onaylandı.")

    def view_password_change_requests():
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE password_change_requested = 1")
        users = cursor.fetchall()
        conn.close()

        for user in users:
            username = user[0]
            ttk.Button(admin_dashboard, text=f"{username} - Onayla", command=lambda u=username: approve_password_change(u)).pack(pady=5)

    # Şifre değiştirme taleplerini göster
    view_password_change_requests_button = ttk.Button(admin_dashboard, text="Parola Değiştirme Taleplerini Gör", command=view_password_change_requests)
    view_password_change_requests_button.pack(pady=10)
    
    def update_storage_limit():

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users")
        usernames = [username[0] for username in cursor.fetchall()]

        storage_limit_combobox = ttk.Combobox(admin_dashboard, values=usernames, state="readonly", width=30)
        storage_limit_combobox.pack(pady=10)

        storage_limit_text = ttk.Entry(admin_dashboard)
        storage_limit_text.pack(pady=10)

        def on_update_button_click():
            selected_username = storage_limit_combobox.get()

            try:
                new_limit = int(storage_limit_text.get())
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir sayı girin.")
                return
            
            cursor.execute("SELECT id FROM users WHERE username = ?", (selected_username,))
            user_id_result = cursor.fetchone()

            if user_id_result:
                user_id = user_id_result[0]
                a.Admin.set_storage_limit(user_id, int(new_limit))
                messagebox.showinfo("Bilgi", f"{user_id} id'li kullanıcının depolama limiti {new_limit} oldu!")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")

        update_storage_limit_button = ttk.Button(admin_dashboard, text="Depolama Limitini Değiştir", command=on_update_button_click)
        update_storage_limit_button.pack(pady=10)
        
    storage_limit_button = ttk.Button(admin_dashboard, text = "Depolama Limitlerini Yönet", command=update_storage_limit)
    storage_limit_button.pack(pady=10)
    
    admin_dashboard.mainloop()
    

def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')
