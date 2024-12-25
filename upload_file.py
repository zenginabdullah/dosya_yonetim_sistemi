import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import shutil
from user_dashboard import *
from tkinter import ttk, Label
from PIL import ImageTk, Image

def upload_file(team_combobox, username):
    """File upload functionality with a modernized UI."""
    selected_team_name = team_combobox.get()  # Get selected team name from combobox
    selected_team_id = None
    
    teams = get_user_teams(username)  # Get user's teams
    for team in teams:
        if team[1] == selected_team_name:
            selected_team_id = team[0]  # Get team ID

    if not selected_team_id:
        messagebox.showerror("Hata", "Geçersiz takım seçildi.")
        return
    
    file_path = filedialog.askopenfilename(title="Dosya Seç", filetypes=[("All Files", "*.*")])
    
    if file_path:
        file_name = file_path.split("/")[-1]  # Extract file name

        try:
            # Insert file info into the database
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            
            cursor.execute(''' 
                INSERT INTO files (user_id, file_name, backup_path, team_id) 
                VALUES (?, ?, ?, ?) 
            ''', (1, file_name, file_path, selected_team_id))  # Use actual user ID

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarı", f"{file_name} dosyası başarıyla yüklendi.")
        except sqlite3.Error as e:
            messagebox.showerror("Veritabanı Hatası", f"Veritabanı hatası: {e}")

def share_file_with_team(file_id, team_id):
    """Share uploaded file with team members."""
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
    """View files shared within the team."""
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
    """Retrieve all teams the user is part of."""
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
    """Retrieve all files uploaded by the team."""
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

def download_file(file_path):
    """Download the selected file."""
    try:
        save_path = filedialog.asksaveasfilename(initialfile=file_path.split("/")[-1])
        if save_path:
            shutil.copy(file_path, save_path)
            messagebox.showinfo("Başarı", "Dosya başarıyla indirildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya indirilirken hata oluştu: {e}")

def open_file_management_panel(username):
    """Open the file management panel with a modernized UI."""
    file_window = tk.Toplevel()
    file_window.title(f"Dosya Yönetim Paneli: {username}")
    file_window.geometry("600x400")
    file_window.configure(bg="#f5f5f5")  # Set a background color for the window
    file_window.resizable(False, False)
    # Style configuration
    style = ttk.Style(file_window)
    style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10), padding=10)
    style.configure("TLabel", font=("Arial", 12), background="#f5f5f5")

    # Add title label
    tk.Label(file_window, text=f"Hoş geldiniz, {username}!", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=10)

    teams = get_user_teams(username)
    team_names = [team[1] for team in teams]  # Team names
    team_ids = {team[1]: team[0] for team in teams}  # Map team name to team ID

    selected_team = tk.StringVar()
    team_combobox = ttk.Combobox(file_window, textvariable=selected_team, values=team_names, state="readonly", width=30)
    team_combobox.set("Takım Seçiniz")  # Default prompt
    team_combobox.pack(pady=10)

    file_list = ttk.Treeview(file_window, columns=("File Name", "Actions"), show="headings", height=10)
    file_list.heading("File Name", text="Dosya Adı")
    file_list.heading("Actions", text="İndir")
    file_list.column("File Name", width=300)
    file_list.column("Actions", width=100)
    file_list.pack(pady=20)

    def refresh_file_list():
        """Refresh the file list for the selected team."""
        file_list.delete(*file_list.get_children())
        selected_team_name = team_combobox.get()
        if selected_team_name != "Takım Seçiniz":
            team_id = team_ids[selected_team_name]
            files = get_team_files(team_id)
            for file_id, file_name, file_path in files:
                file_list.insert("", "end", values=(file_name, "İndir"), tags=(file_path,))

    def on_file_select(event):
        """Handle file download on item selection."""
        item = file_list.selection()[0]
        file_path = file_list.item(item, "tags")[0]
        download_file(file_path)

    file_list.bind("<Double-1>", on_file_select)

    # Buttons to upload, refresh, etc.
    tk.Button(file_window, text="Dosya Yükle", command=lambda: upload_file(team_combobox, username)).pack(pady=10)
    tk.Button(file_window, text="Listeyi Yenile", command=refresh_file_list).pack(pady=5)

    # Bind event to refresh file list when team is selected
    team_combobox.bind("<<ComboboxSelected>>", lambda e: refresh_file_list())

    file_window.mainloop()
