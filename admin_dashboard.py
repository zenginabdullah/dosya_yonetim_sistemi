import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import admin as a
import user
import os

def open_admin_dashboard(username):
    admin_dashboard = tk.Toplevel()
    admin_dashboard.title(f"Admin Paneli: {username}")
    admin_dashboard.geometry("500x500")
    admin_dashboard.configure(bg="#f2f2f2")
    center_window(admin_dashboard, 500, 500)

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
        # Yeni pencere oluştur
        update_limit_window = tk.Toplevel()
        update_limit_window.title("Depolama Limitini Güncelle")
        update_limit_window.geometry("350x250")
        update_limit_window.configure(bg="#f2f2f2")
        center_window(update_limit_window, 350, 250)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        # Kullanıcı adlarını getir
        cursor.execute("SELECT username FROM users")
        usernames = [username[0] for username in cursor.fetchall()]
        conn.close()

        if not usernames:
            messagebox.showinfo("Bilgi", "Hiç kullanıcı bulunamadı.")
            update_limit_window.destroy()
            return

        # Kullanıcı seçimi için ComboBox
        ttk.Label(update_limit_window, text="Kullanıcı Seçiniz:", background="#f2f2f2").pack(pady=10)
        storage_limit_combobox = ttk.Combobox(update_limit_window, values=usernames, state="readonly", width=30)
        storage_limit_combobox.pack(pady=10)
        storage_limit_combobox.set("Kullanıcı Seçiniz")

        # Yeni limit girişi
        ttk.Label(update_limit_window, text="Yeni Depolama Limiti:", background="#f2f2f2").pack(pady=10)
        storage_limit_text = ttk.Entry(update_limit_window)
        storage_limit_text.pack(pady=10)

        # Depolama limitini güncelle
        def on_update_button_click():
            selected_username = storage_limit_combobox.get()

            try:
                new_limit = int(storage_limit_text.get())
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir sayı girin.")
                return
            
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (selected_username,))
            user_id_result = cursor.fetchone()
            conn.close()

            if user_id_result:
                user_id = user_id_result[0]
                a.Admin.set_storage_limit(user_id, new_limit)
                messagebox.showinfo("Bilgi", f"{user_id} id'li kullanıcının depolama limiti {new_limit} oldu!")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
                return

            # Pencereyi kapat
            update_limit_window.destroy()

        ttk.Button(update_limit_window, text="Depolama Limitini Güncelle", command=on_update_button_click).pack(pady=20)

        
    storage_limit_button = ttk.Button(admin_dashboard, text = "Depolama Limitlerini Yönet", command=update_storage_limit)
    storage_limit_button.pack(pady=10)
    
    def delete_user_dashboard():
        delete_user_dashboard = tk.Toplevel()
        delete_user_dashboard.title("Kullanıcı Sil")
        delete_user_dashboard.geometry("300x200")
        delete_user_dashboard.configure(bg="#f2f2f2")
        center_window(delete_user_dashboard, 300, 200)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        conn.close()

        if not users:
            messagebox.showinfo("Bilgi", "Sistemde hiçbir kullanıcı bulunmamaktadır.")
            delete_user_dashboard.destroy()
            return

        selected_user = tk.StringVar()
        delete_combobox = ttk.Combobox(delete_user_dashboard, textvariable=selected_user, state="readonly", width=25)
        delete_combobox['values'] = [f"{user[1]} (ID: {user[0]})" for user in users]
        delete_combobox.pack(pady=20)
        delete_combobox.set("Kullanıcı Seçiniz")

        def confirm_delete():
            selected = selected_user.get()
            if not selected or selected == "Kullanıcı Seçiniz":
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçiniz.")
                return

            user_id = int(selected.split("(ID: ")[1].strip(")"))
            a.Admin.delete_user(user_id)

            delete_combobox['values'] = [user for user in delete_combobox['values'] if f"(ID: {user_id})" not in user]
            if len(delete_combobox['values']) == 0:
                delete_combobox.set("Hiç kullanıcı kalmadı.")
            else:
                delete_combobox.set("Kullanıcı Seçiniz")

        delete_button = ttk.Button(delete_user_dashboard, text="Sil", command=confirm_delete)
        delete_button.pack(pady=10)
    
    delete_user_button = ttk.Button(admin_dashboard, text = "Kullanıcı Sil", command=delete_user_dashboard)
    delete_user_button.pack(pady=10)
    
    def view_encrypted_password_dashboard():
        # Yeni bir pencere oluştur
        password_window = tk.Toplevel()
        password_window.title("Şifreyi Görüntüle")
        password_window.geometry("350x200")
        password_window.configure(bg="#f2f2f2")
        center_window(password_window, 350, 200)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        # Kullanıcı ID'lerini al
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        conn.close()

        if not users:
            messagebox.showinfo("Bilgi", "Hiçbir kullanıcı bulunamadı.")
            password_window.destroy()
            return

        # Kullanıcı seçimi için ComboBox
        ttk.Label(password_window, text="Kullanıcı Seçiniz:", background="#f2f2f2").pack(pady=10)
        user_combobox = ttk.Combobox(password_window, state="readonly", width=30)
        user_combobox['values'] = [f"{user[1]} (ID: {user[0]})" for user in users]
        user_combobox.pack(pady=10)
        user_combobox.set("Kullanıcı Seçiniz")

        def show_password():
            selected_user = user_combobox.get()
            if not selected_user or selected_user == "Kullanıcı Seçiniz":
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçiniz.")
                return
            
            user_id = int(selected_user.split("(ID: ")[1].strip(")"))
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                messagebox.showinfo("Şifre", f"Kullanıcının Şifrelenmiş Parolası: {result[0]}")
            else:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")

        # Şifre görüntüleme butonu
        ttk.Button(password_window, text="Şifreyi Görüntüle", command=show_password).pack(pady=20)
    
    view_password_button = ttk.Button(admin_dashboard, text="Şifre Görüntüle", command=view_encrypted_password_dashboard)
    view_password_button.pack(pady=10)
    
    def view_logs_dashboard():
        # Yeni bir pencere oluştur
        logs_window = tk.Toplevel()
        logs_window.title("Logları Görüntüle")
        logs_window.geometry("350x150")
        logs_window.configure(bg="#f2f2f2")
        center_window(logs_window, 350, 150)

        def export_logs():
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, user_id, action FROM logs ORDER BY timestamp DESC")
            logs = cursor.fetchall()
            conn.close()

            if logs:
                # Logları dosyaya kaydet
                log_details = "\n".join([f"Tarih: {log[0]}, Kullanıcı ID: {log[1]}, İşlem: {log[2]}" for log in logs])
                with open("logs.txt", "w", encoding="utf-8") as log_file:
                    log_file.write("Sistem Logları\n")
                    log_file.write("=" * 50 + "\n")
                    log_file.write(log_details)
                
                messagebox.showinfo("Log Dosyaları", "Loglar 'logs.txt' dosyasına başarıyla kaydedildi.")
            else:
                messagebox.showinfo("Log Dosyaları", "Hiçbir işlem kaydı bulunamadı.")

        # Logları dışa aktar butonu
        ttk.Button(logs_window, text="Logları Dışa Aktar", command=export_logs).pack(pady=20)

    view_logs_button = ttk.Button(admin_dashboard, text="Logları Görüntüle", command=view_logs_dashboard)
    view_logs_button.pack(pady=10)

    def view_user_files_dashboard():
        # Yeni bir pencere oluştur
        files_window = tk.Toplevel()
        files_window.title("Kullanıcı Dosyalarını Görüntüle")
        files_window.geometry("500x500")
        files_window.configure(bg="#f2f2f2")
        center_window(files_window, 500, 500)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        # Kullanıcı ID'lerini ve adlarını al
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        conn.close()

        if not users:
            messagebox.showinfo("Bilgi", "Hiçbir kullanıcı bulunamadı.")
            files_window.destroy()
            return

        # Kullanıcı seçimi için ComboBox
        ttk.Label(files_window, text="Kullanıcı Seçiniz:", background="#f2f2f2").pack(pady=10)
        user_combobox = ttk.Combobox(files_window, state="readonly", width=40)
        user_combobox['values'] = [f"{user[1]} (ID: {user[0]})" for user in users]
        user_combobox.pack(pady=10)
        user_combobox.set("Kullanıcı Seçiniz")

        # Dosyaları listelemek için bir liste
        file_listbox = tk.Listbox(files_window, width=60, height=15)
        file_listbox.pack(pady=10)

        def load_user_files():
            # Kullanıcı seçimini al
            selected_user = user_combobox.get()
            if not selected_user or selected_user == "Kullanıcı Seçiniz":
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçiniz.")
                return

            user_id = int(selected_user.split("(ID: ")[1].strip(")"))
            
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, file_name, backup_path, created_at FROM files WHERE user_id = ?", (user_id,))
            files = cursor.fetchall()
            conn.close()

            # Listeyi temizle ve yeni verileri ekle
            file_listbox.delete(0, tk.END)
            if files:
                for file in files:
                    file_listbox.insert(tk.END, f"Dosya: {file[1]} | Yedekleme Yolu: {file[2]} | Tarih: {file[3]}")
            else:
                messagebox.showinfo("Bilgi", "Bu kullanıcıya ait hiçbir dosya bulunamadı.")

        def open_backup_path():
            # Seçili dosyanın yedekleme yolunu al
            selected_file = file_listbox.get(tk.ACTIVE)
            if not selected_file:
                messagebox.showerror("Hata", "Lütfen bir dosya seçiniz.")
                return

            backup_path = selected_file.split("| Yedekleme Yolu: ")[1].split(" |")[0]
            try:
                os.startfile(backup_path)  # Windows için yedekleme yolunu açar
            except Exception as e:
                messagebox.showerror("Hata", f"Yedekleme yolu açılamadı. Hata: {e}")

        # Kullanıcı dosyalarını listeleme butonu
        ttk.Button(files_window, text="Dosyaları Yükle", command=load_user_files).pack(pady=10)
        
        # Seçili dosyanın yedekleme yolunu açma butonu
        ttk.Button(files_window, text="Yedekleme Yolunu Aç", command=open_backup_path).pack(pady=10)
        
    view_files_button = ttk.Button(admin_dashboard, text="Kullanıcı Dosyalarını Görüntüle", command=view_user_files_dashboard)
    view_files_button.pack(pady=10)

    def set_role_dashboard():
        set_role_window = tk.Toplevel()
        set_role_window.title("Kullanıcı Yetkilerini Düzenle")
        set_role_window.geometry("500x500")
        set_role_window.configure(bg="#f2f2f2")
        center_window(set_role_window, 500, 500)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        # Kullanıcı ID'lerini ve adlarını al
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        conn.close()

        if not users:
            messagebox.showinfo("Bilgi", "Hiçbir kullanıcı bulunamadı.")
            set_role_window.destroy()
            return

        # Kullanıcı seçimi için ComboBox
        ttk.Label(set_role_window, text="Kullanıcı Seçiniz:", background="#f2f2f2").pack(pady=10)
        user_combobox = ttk.Combobox(set_role_window, state="readonly", width=40)
        user_combobox['values'] = [f"{user[1]}" for user in users]
        user_combobox.pack(pady=10)
        user_combobox.set("Kullanıcı Seçiniz")

        # Yetki seçimi için ComboBox
        ttk.Label(set_role_window, text="Yetki Seçiniz:", background="#f2f2f2").pack(pady=10)
        role_combobox = ttk.Combobox(set_role_window, state="readonly", width=40)
        role_combobox['values'] = ['admin', 'user']
        role_combobox.pack(pady=10)
        role_combobox.set("Yetki Seçiniz")

        # "Rolü Düzenle" butonunu tıklayınca rolü ayarlayan işlem
        def on_role_set():
            selected_user = user_combobox.get()
            selected_role = role_combobox.get()

            # Kullanıcı seçimi ve rol seçim kontrolü
            if selected_user == "Kullanıcı Seçiniz":
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçiniz.")
                return

            if selected_role == "Yetki Seçiniz":
                messagebox.showerror("Hata", "Lütfen bir yetki seçiniz.")
                return

            # Kullanıcı ID'sini al
            user_id = user.User.get_user_id(selected_user)
            if user_id is None:
                messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
                return

            # Rolü ayarla
            a.Admin.set_role(user_id, selected_role)
            messagebox.showinfo("Başarılı", f"{selected_user} kullanıcısının rolü başarıyla {selected_role} olarak ayarlandı.")

        # Kullanıcı rolünü ayarlamak için buton
        ttk.Button(set_role_window, text="Rolü Düzenle", command=on_role_set).pack(pady=10)


    set_role_button = ttk.Button(admin_dashboard, text="Kullanıcı Rollerini Yönet", command=set_role_dashboard)
    set_role_button.pack(pady=10)
    
    admin_dashboard.mainloop()
def center_window(window, width, height):
    window.geometry(f'{width}x{height}+{(window.winfo_screenwidth() // 2) - (width // 2)}+{(window.winfo_screenheight() // 2) - (height // 2)}')

