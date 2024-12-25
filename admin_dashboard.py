import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

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

    admin_dashboard.mainloop()

def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')
