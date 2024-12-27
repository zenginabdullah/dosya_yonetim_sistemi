import sqlite3
from tkinter import messagebox
import json

db_path = "app.db"

class Admin:
    
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.team_members = []
        self.shared_files = []
        
    def add_team_member(user_id, team_member_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Mevcut takım üyelerini çek
        cursor.execute("SELECT team_members FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        current_members = json.loads(result[0]) if result[0] else []

        if team_member_id in current_members:
            messagebox.showwarning("Hata", "Bu kullanıcı zaten takım üyesi.")
            return

        # Takım üyelerini güncelle
        current_members.append(team_member_id)
        updated_members = json.dumps(current_members)
        cursor.execute("UPDATE users SET team_members = ? WHERE id = ?", (updated_members, user_id))
        
        # Bildirim gönder
        cursor.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", 
                    (team_member_id, f"{user_id} sizi takım üyesi olarak ekledi."))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Takım üyesi başarıyla eklendi.")
    
    def approve_password_request(request_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Talebi onayla
        cursor.execute("UPDATE password_requests SET status = 'approved' WHERE id = ?", (request_id,))
        conn.commit()
        
        # Talep edilen kullanıcıya bildirim gönder
        cursor.execute("SELECT user_id FROM password_requests WHERE id = ?", (request_id,))
        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", 
                    (user_id, "Parola değişikliği talebiniz onaylandı."))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Parola değiştirme talebi onaylandı.")

    def set_storage_limit(user_id, new_limit):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE users SET storage_limit = ? WHERE id = ?", (new_limit, user_id))
            conn.commit()
        else:
            messagebox.showerror("Hata", f"Kullanıcı ID {user_id} bulunamadı.")
            return
        
    def delete_user(user_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Kullanıcı başarıyla silindi.")
        else:
            conn.close()
            messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
    
    def view_encrypted_password(user_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Şifre", f"Kullanıcının Şifrelenmiş Parolası: {result[0]}")
        else:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
    
    def view_logs():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, user_id, action FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()

        if logs:
            # Logları metin formatına dönüştür
            log_details = "\n".join([f"Tarih: {log[0]}, Kullanıcı ID: {log[1]}, İşlem: {log[2]}" for log in logs])
            
            # Logları bir dosyaya yaz
            with open("logs.txt", "w", encoding="utf-8") as log_file:
                log_file.write("Sistem Logları\n")
                log_file.write("=" * 50 + "\n")
                log_file.write(log_details)
            
            messagebox.showinfo("Log Dosyaları", f"Tüm loglar 'logs.txt' dosyasına başarıyla kaydedildi.")
        else:
            messagebox.showinfo("Log Dosyaları", "Hiçbir işlem kaydı bulunamadı.")
