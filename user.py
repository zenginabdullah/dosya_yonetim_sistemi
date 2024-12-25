import sqlite3
from tkinter import messagebox
import bcrypt

db_path = "app.db"

class User:
    
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.team_members = []
        self.shared_files = []

    def register(self, username, password):
        pass
    
    def change_username(username, new_username):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, username))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", f"Kullanıcı adı '{new_username}' olarak güncellendi!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")

    def request_password_change(user_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO password_requests (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Talep Gönderildi", "Parola değiştirme talebiniz sistem yöneticisine iletildi.")

    def change_password(username, new_password):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        conn.close()
        messagebox.showinfo("Parolanız başarıyla değiştirildi.")
        
    def get_user_id(username):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]
        
        return user_id
