import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter import Label
from PIL import Image, ImageTk
from logger import log_action
import user
import datetime

def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')

def open_team_management(username, dashboard):
    team_window = tk.Toplevel()
    team_window.title("Takım Yönetimi")
    team_window.geometry("400x500")
    team_window.resizable(False, False)
    center_window(team_window, 400, 500)

    team_resim = Image.open("photos/team.png")
    team_resim = team_resim.resize((100, 100))
    team_resim = ImageTk.PhotoImage(team_resim)
    tresim = Label(team_window,image=team_resim)
    tresim.place(x=10,y=10)
    tresim.image = team_resim
    tresim.pack(pady=10)
    
    # Stil için ttk.LabelFrame kullanımı
    frame = ttk.LabelFrame(team_window, text="Takım Yönetimi", padding=(10, 10))
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Takım adı girişi
    ttk.Label(frame, text="Takım Adı:", font=("Arial", 12)).pack(pady=10)
    entry_team_name = ttk.Entry(frame, width=30)
    entry_team_name.pack(pady=5)

    # Takım oluşturma işlemi
    def create_team():
        team_name = entry_team_name.get()
        if team_name:
            try:
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO teams (team_name, creator) VALUES (?, ?)", (team_name, username))
                conn.commit()
                user_id = user.User.get_user_id(username)
                messagebox.showinfo("Başarı", f"{team_name} takımı oluşturuldu.")
                log_action(user_id, "Takım Oluşturma", f"{username} kullanıcısı tarafından {team_name} takımı oluşturuldu.")

                cursor.execute("SELECT id FROM teams WHERE team_name = ?", (team_name,))
                team_result = cursor.fetchone()

                if team_result:
                    team_id = team_result[0]
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    user_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO team_members (team_id, user_id) VALUES (?, ?)", (team_id, user_id))
                    conn.commit()

                conn.close()
                team_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası: {e}")
        else:
            messagebox.showwarning("Hata", "Takım adı boş olamaz.")

    ttk.Button(frame, text="Takım Oluştur", command=create_team).pack(pady=20)

    # Takım üyelerini görüntüleme ve ekleme
    def view_and_add_members():
        members_window = tk.Toplevel()
        members_window.title("Takım Üyeleri")
        members_window.geometry("400x400")
        center_window(members_window, 400, 400)

        members_frame = ttk.LabelFrame(members_window, text="Takım Üyeleri", padding=(10, 10))
        members_frame.pack(padx=20, pady=20, fill="both", expand=True)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username != ?", (username,))
        members = cursor.fetchall()
        conn.close()

        listbox = tk.Listbox(members_frame, height=10, width=30, selectmode=tk.SINGLE)
        listbox.pack(pady=10)

        for member in members:
            listbox.insert(tk.END, member[1])

        def add_member_to_team():
            team_name = entry_team_name.get()
            selected_member = listbox.get(tk.ACTIVE)
            if selected_member:
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM teams WHERE team_name = ?", (team_name,))
                team_result = cursor.fetchone()

                if team_result:
                    team_id = team_result[0]
                    cursor.execute("SELECT id FROM users WHERE username = ?", (selected_member,))
                    user_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO team_members (team_id, user_id) VALUES (?, ?)", (team_id, user_id))
                    conn.commit()

                    messagebox.showinfo("Başarı", f"{selected_member} takıma eklendi.")
                    log_action(user_id, "Takım Üyesi Ekleme", f"{selected_member} adlı kullanıcı {team_name} takımına eklendi.")
                    cursor.execute('''INSERT INTO notifications (user_id, message)VALUES (?, ?)''', (user_id, f"{team_name} takımına eklendiniz."))
                    conn.commit()
                else:
                    messagebox.showwarning("Hata", f"{team_name} adlı takım bulunamadı.")
                    conn.close()
            else:
                messagebox.showwarning("Hata", "Bir üye seçmelisiniz.")

        ttk.Button(members_frame, text="Üye Ekle", command=add_member_to_team).pack(pady=10)

    ttk.Button(frame, text="Takım Üyelerini Görüntüle ve Ekle", command=view_and_add_members).pack(pady=20)
    ttk.Button(team_window, text="Çıkış", command=team_window.destroy).pack(pady=10)
    # Arka plan rengi ve yazı fontu
    team_window.configure(bg="#f0f0f0")
