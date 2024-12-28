import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import shutil
from user_dashboard import *
from tkinter import ttk, Label, Toplevel
from PIL import ImageTk, Image
from logger import log_action
import user
from file_sync import *

global logged_user

def upload_file(team_combobox, username):
    selected_team_name = team_combobox.get()
    selected_team_id = None
    
    teams = get_user_teams(username)
    for team in teams:
        if team[1] == selected_team_name:
            selected_team_id = team[0]

    if not selected_team_id:
        messagebox.showerror("Hata", "Geçersiz takım seçildi.")
        return
    
    file_path = filedialog.askopenfilename(title="Dosya Seç", filetypes=[("All Files", "*.*")])
    user_id = user.User.get_user_id(username)
    if file_path:
        file_name = file_path.split("/")[-1]

        try:

            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            
            cursor.execute(''' 
                INSERT INTO files (user_id, file_name, backup_path, team_id) 
                VALUES (?, ?, ?, ?) 
            ''', (user_id, file_name, file_path, selected_team_id))

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarı", f"{file_name} dosyası başarıyla yüklendi.")
            shutil.copy(file_path, "source")
            log_action(user_id, "Dosya Yükleme", f"{username} tarafında {selected_team_name} takımına {file_name} dosyası yüklendi.")
        except sqlite3.Error as e:
            messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası: {e}")

def share_file_with_team(file_id, team_id):

    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute('''SELECT user_id FROM team_members WHERE team_id = ?''', (team_id,))
        team_members = cursor.fetchall()

        for member in team_members:
            user_id = member[0]
            cursor.execute('''INSERT INTO notifications (user_id, message) VALUES (?, ?)''', 
                           (user_id, f"Yeni bir dosya paylaşıldı: {file_id}"))

        conn.commit()
        conn.close()
        messagebox.showinfo("Başarı", "Dosya takıma başarıyla paylaşıldı.")
    except sqlite3.Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası: {e}")

def view_shared_files(team_id):

    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT files.file_name, files.backup_path
            FROM files
            JOIN team_members ON files.user_id = team_members.user_id
            WHERE team_members.team_id = ?
        ''', (team_id,))
        shared_files = cursor.fetchall()

        # Display the shared files in a list
        for file in shared_files:
            print(f"Dosya Adı: {file[0]}, Dosya Yolu: {file[1]}")
        
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası: {e}")

def get_user_teams(username):

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT teams.id, teams.team_name
        FROM teams
        JOIN team_members ON teams.id = team_members.team_id
        JOIN users ON team_members.user_id = users.id
        WHERE users.username = ?
    ''', (username,))

    teams = cursor.fetchall()
    conn.close()
    
    return teams

def get_team_files(team_id):

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, file_name, backup_path
        FROM files
        WHERE team_id = ?
    ''', (team_id,))

    files = cursor.fetchall()
    conn.close()

    return files

def ask_custom_action():
    action_window = tk.Toplevel()
    action_window.title("Seçim Yapın")
    action_window.geometry("300x150")
    action_window.resizable(False, False)

    label = tk.Label(action_window, text="Dosya ile ne yapmak istersiniz?", font=("Arial", 12))
    label.pack(pady=10)

    result = {"choice": None}

    def select_action(choice):
        result["choice"] = choice
        action_window.destroy()

    edit_button = tk.Button(action_window, text="Düzenle", font=("Arial", 10), bg="lightblue", command=lambda: select_action("edit"))
    edit_button.pack(side="left", padx=20, pady=20)

    download_button = tk.Button(action_window, text="İndir", font=("Arial", 10), bg="lightgreen", command=lambda: select_action("download"))
    download_button.pack(side="right", padx=20, pady=20)

    action_window.wait_window()

    return result["choice"]

def download_file(file_path, username):

    try:
        action = ask_custom_action()
        
        if action == "edit":
            open_edit_file_content_panel(file_path, username)
        elif action == "download":
            save_path = filedialog.asksaveasfilename(initialfile=file_path.split("/")[-1])
            if save_path:
                shutil.copy(file_path, save_path)
                messagebox.showinfo("Başarı", "Dosya başarıyla indirildi.")
                
                user_id = user.User.get_user_id(username)
                log_action(user_id, "Dosya İndirme", f"{username} kullanıcısı {file_path} dosyasını indirdi.")
        else:
            messagebox.showinfo("İptal", "Hiçbir işlem yapılmadı.")
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya indirilirken hata oluştu: {e}")


def open_edit_file_content_panel(file_path, username):

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
        return
    
    edit_window = tk.Toplevel()
    edit_window.title("Dosya İçeriğini Düzenle")
    edit_window.geometry("600x550")
    edit_window.configure(bg="#f5f5f5")
    
    text_frame = tk.Frame(edit_window)
    text_frame.pack(expand=True, fill="both", padx=10, pady=10)

    text_area = tk.Text(text_frame, wrap="word", font=("Arial", 12), undo=True)
    text_area.pack(expand=True, fill="both")
    text_area.insert("1.0", file_content)

    button_frame = tk.Frame(edit_window, bg="#f5f5f5")
    button_frame.pack(fill="x", padx=10, pady=10)

    def save_file():

        new_content = text_area.get("1.0", "end-1c")
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            messagebox.showinfo("Başarı", "Dosya içeriği başarıyla kaydedildi.")
            auto_backup_and_sync(file_path)
            user_id = user.User.get_user_id(username)
            log_action(user_id, "Dosya Düzenleme", f"{username} kullanıcısı {file_path} dosyasını düzenledi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {e}")

    save_button = tk.Button(button_frame, text="Kaydet", command=save_file, bg="#4CAF50", fg="white", font=("Arial", 12))
    save_button.pack(pady=10, side="bottom")