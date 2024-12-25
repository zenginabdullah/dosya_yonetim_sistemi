import sqlite3
from tkinter import messagebox 
import bcrypt


def create_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('user', 'admin')) NOT NULL,
            storage_limit INTEGER DEFAULT 1024, -- MB cinsinden depolama limiti
            team_members TEXT DEFAULT NULL, -- JSON formatında takım üyeleri
            password_change_requested BOOLEAN DEFAULT 0
        )
    ''')

    # Dosyalar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            backup_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
        )
    ''')
    

    # Loglar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Bildirimler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Parola değiştirme talepleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Anomaliler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            creator TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            team_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def register(username, password, role):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        messagebox.showerror("", f"Hata: '{username}' kullanıcı adı mevcut!")
    else:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
        messagebox.showinfo("", "Kayıt başarılı!")
    conn.commit()
    conn.close()

create_db()
