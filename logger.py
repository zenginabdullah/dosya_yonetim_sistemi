import sqlite3
from tkinter import messagebox

def log_action(user_id=0, action="Bilinmiyor", details=None):
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute(''' 
            INSERT INTO logs (user_id, action, details) 
            VALUES (?, ?, ?) 
        ''', (user_id, action, details))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Log kaydedilirken hata oluştu: {e}")