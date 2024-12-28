import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from user import User
from teams import *
from upload_file import download_file, upload_file, get_user_teams, get_team_files
from tkinter import font


def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')

def open_user_dashboard(username):
    dashboard = tk.Toplevel()
    dashboard.title(f"Kullanıcı Paneli: {username}")
    dashboard.geometry("400x450")
    dashboard.resizable(False, False)
    center_window(dashboard, 400, 450)
    
    # Modern font
    title_font = font.Font(family="Arial", size=18, weight="bold")
    button_font = font.Font(family="Arial", size=12)

    tk.Label(dashboard, text=f"Hoş geldiniz, {username}!", font=title_font).pack(pady=20)

    # Frame for buttons to improve layout
    button_frame = ttk.LabelFrame(dashboard, text="İşlemler", padding=(10,10))
    button_frame.pack(padx=20, pady=10, fill="both", expand=False)

    # Ayarlar sekmesi
    def open_settings():
        settings_window = tk.Toplevel()
        settings_window.title("Ayarlar")
        settings_window.geometry("350x250")
        center_window(settings_window, 350, 250)

        # Kullanıcı adı değiştirme
        def change_username():
            def submit_username_change():
                new_username = entry_new_username.get()
                if new_username:
                    User.change_username(username, new_username)
                    settings_window.destroy()
                    change_window.destroy()
                    dashboard.destroy()
                    open_user_dashboard(new_username)
                else:
                    messagebox.showwarning("Hata", "Yeni kullanıcı adı boş olamaz.")

            change_window = tk.Toplevel()
            change_window.title("Kullanıcı Adı Değiştir")
            change_window.geometry("300x150")
            center_window(change_window, 300, 150)
            
            tk.Label(change_window, text="Yeni Kullanıcı Adı:").pack(pady=5)
            entry_new_username = tk.Entry(change_window)
            entry_new_username.pack(pady=5)
            tk.Button(change_window, text="Değiştir", command=submit_username_change).pack(pady=10)

        # Parola değiştirme isteği
        def request_password_change(username):
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password_change_requested FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == 1:
                messagebox.showwarning("Hata", "Zaten bir parola değiştirme talebi gönderdiniz.")
            elif result and result[0] == 2:
                change_window = tk.Toplevel()
                change_window.title("Şifre Değiştir")
                change_window.geometry("300x150")
                center_window(change_window, 300, 150)
                
                tk.Label(change_window, text="Yeni Parola:").pack(pady=5)
                entry_new_password = tk.Entry(change_window)
                entry_new_password.pack(pady=5)
                tk.Button(change_window, text="Değiştir", 
                        command=lambda: User.change_password(username, entry_new_password.get())).pack(pady=10)
            else:
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_change_requested = 1 WHERE username = ?", (username,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Talep Gönderildi", "Parola değiştirme talebiniz gönderildi.")

        # Ayarlar penceresinde butonlar
        settings_button_frame = ttk.LabelFrame(settings_window, text="Kullanıcı Ayarları", padding=(10,10))
        settings_button_frame.pack(padx=20, pady=10, fill="both", expand=False)
        
        ttk.Button(settings_button_frame, text="Kullanıcı Adı Değiştir", command=change_username, width=20).pack(pady=10)
        ttk.Button(settings_button_frame, text="Parola Değiştirme Talebi Gönder", command=lambda: request_password_change(username)).pack(pady=10)
        ttk.Button(settings_window, text="Çıkış", command=settings_window.destroy).pack(pady=10)
        
    def open_files(username):
        file_window = tk.Toplevel()
        file_window.title(f"Dosya Yönetim Paneli: {username}")
        file_window.geometry("600x600")
        center_window(file_window, 600, 600)

        file_resim = Image.open("photos/file.png")
        file_resim = file_resim.resize((100, 100))
        file_resim = ImageTk.PhotoImage(file_resim)
        fresim = Label(file_window,image=file_resim)
        fresim.place(x=10,y=10)
        fresim.image = file_resim
        fresim.pack(pady=10)
    
        teams = get_user_teams(username)
        team_names = [team[1] for team in teams]
        team_ids = {team[1]: team[0] for team in teams}

        selected_team = tk.StringVar()
        team_combobox = ttk.Combobox(file_window, textvariable=selected_team, values=team_names, state="readonly", width=25)
        team_combobox.pack(pady=10)
        team_combobox.set("Takım Seçiniz")

        file_list = ttk.Treeview(file_window, columns=("File Name", "Actions"), show="headings", height=10)
        file_list.heading("File Name", text="Dosya Adı")
        file_list.heading("Actions", text="İndir")
        file_list.column("File Name", width=300)
        file_list.column("Actions", width=100)
        file_list.pack(pady=10)

        def refresh_file_list():
            file_list.delete(*file_list.get_children())
            selected_team_name = team_combobox.get()
            if selected_team_name and selected_team_name != "Takım Seçiniz":
                team_id = team_ids[selected_team_name]
                files = get_team_files(team_id)
                for file_id, file_name, file_path in files:
                    file_list.insert("", "end", values=(file_name, "İndir"), tags=(file_path,))

        def on_file_select(event):
            item = file_list.selection()[0]
            file_path = file_list.item(item, "tags")[0]
            download_file(file_path, username)

        file_list.bind("<Double-1>", on_file_select)

        ttk.Button(file_window, text="Dosya Yükle", command=lambda: upload_file(team_combobox, username), width=20).pack(pady=10)
        ttk.Button(file_window, text="Listeyi Yenile", command=refresh_file_list, width=20).pack(pady=5)
        ttk.Button(file_window, text="Çıkış", command=file_window.destroy).pack(pady=10)

        team_combobox.bind("<<ComboboxSelected>>", lambda e: refresh_file_list())
        
    def show_notifications(username):
        notification_window = tk.Toplevel()
        notification_window.title(f"Bildirim Paneli: {username}")
        notification_window.geometry("600x550")
        center_window(notification_window, 600, 550)

        notification_resim = Image.open("photos/notification.png")
        notification_resim = notification_resim.resize((100, 100))
        notification_resim = ImageTk.PhotoImage(notification_resim)
        nresim = Label(notification_window,image=notification_resim)
        nresim.place(x=10,y=10)
        nresim.image = notification_resim
        nresim.pack(pady=10)
        
        notification_list = ttk.Treeview(notification_window, columns=("Notification", "Created At"), show="headings", height=15)
        notification_list.heading("Notification", text="Bildirim")
        notification_list.heading("Created At", text="Tarih")
        notification_list.column("Notification", width=300)
        notification_list.column("Created At", width=150)
        notification_list.pack(pady=10)
        
        def load_notifications(notification_list, user_id):
            """Belirli bir kullanıcı için bildirimleri Treeview'e yükler."""
            connection = sqlite3.connect("app.db")
            cursor = connection.cursor()
            try:
                cursor.execute('''
                    SELECT id, message, created_at
                    FROM notifications
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                notifications = cursor.fetchall()

                # Mevcut listeyi temizle
                for row in notification_list.get_children():
                    notification_list.delete(row)

                # Bildirimleri Treeview'e ekle
                for notification_id, message, created_at in notifications:
                    # Tarihi okunabilir formata dönüştür
                    readable_date = created_at  # Doğrudan kullanabiliriz çünkü datetime formatında
                    # Treeview'e eklerken iid olarak notification_id kullanıyoruz
                    notification_list.insert("", "end", iid=str(notification_id), values=(message, readable_date))

            except Exception as e:
                print(f"Bildirimleri yüklerken hata oluştu: {e}")
            finally:
                connection.close()

        def delete_notification(notification_list, user_id):
            """Seçilen bildirimi siler."""
            selected_item = notification_list.selection()
            if not selected_item:
                messagebox.showwarning("Uyarı", "Silmek için bir bildirim seçin!")
                return

            notification_id = selected_item[0]  # Seçilen bildirim ID'si (str olarak alınır)
            confirm = messagebox.askyesno("Onay", "Bu bildirimi silmek istiyor musunuz?")
            if confirm:
                connection = sqlite3.connect("app.db")
                cursor = connection.cursor()
                try:
                    # Bildirimi veritabanından sil
                    cursor.execute('DELETE FROM notifications WHERE id = ? AND user_id = ?', (notification_id, user_id))
                    connection.commit()  # Değişiklikleri kaydet
                    print(f"Bildirim {notification_id} silindi.")
                    
                    # Treeview'den de kaldır
                    notification_list.delete(notification_id)
                    messagebox.showinfo("Başarılı", "Bildirim silindi.")
                except Exception as e:
                    print(f"Bildirim silinirken hata oluştu: {e}")
                    messagebox.showerror("Hata", "Bildirim silinirken bir hata oluştu.")
                finally:
                    connection.close()

        # Treeview çift tıklama event'i
        def on_notification_double_click(event, notification_list, user_id):
            """Treeview çift tıklama olayını yönetir."""
            delete_notification(notification_list, user_id)
        
        user_id = User.get_user_id(username)
        notification_list.bind("<Double-1>", lambda event: on_notification_double_click(event, notification_list, user_id))
        load_notifications(notification_list, user_id)
        
    ttk.Button(button_frame, text="Ayarlar", command=open_settings, width=20).pack(pady=10)
    ttk.Button(button_frame, text="Dosya Sistemi", command=lambda: open_files(username), width=20).pack(pady=10)
    ttk.Button(button_frame, text="Takım Ayarları", command=lambda: open_team_management(username, dashboard), width=20).pack(pady=10)
    ttk.Button(button_frame, text="Bildirimleri Görüntüle", command=lambda: show_notifications(username), width=20).pack(pady=10)
    ttk.Button(button_frame, text="Çıkış", command=dashboard.quit, width=20).pack(pady=10)
    
    dashboard.mainloop()