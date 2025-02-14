import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinter import ttk

BACKUP_DIR = "backup"
SYNC_DIR = "sync"
SOURCE_DIR = "source"


def ensure_directories():
    """Gerekli dizinleri oluşturur."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(SYNC_DIR, exist_ok=True)
    os.makedirs(SOURCE_DIR, exist_ok=True)

def backup_file(file_path):
    """Dosyayı yedekleme dizinine kopyalar, her dosya için kendi alt klasöründe saklar."""
    ensure_directories()
    if not os.path.isfile(file_path):
        return
    
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]  # Dosya adından uzantıyı ayıkla
    file_folder = os.path.join(BACKUP_DIR, file_base_name)
    
    os.makedirs(file_folder, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(file_folder, f"{file_name}_{timestamp}")
    
    try:
        shutil.copy(file_path, backup_path)
        print(f"{file_name} yedekleme dizinine başarıyla kopyalandı: {backup_path}")
    except Exception as e:
        print(f"Yedekleme sırasında hata oluştu: {e}")

def sync_file(file_path):
    """Yedekleme dizinindeki dosyayı senkronizasyon dizinine kopyalar."""
    ensure_directories()
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]  # Dosya adından uzantıyı ayıkla
    source_folder = os.path.join(BACKUP_DIR, file_base_name)
    destination_path = os.path.join(SYNC_DIR, file_name)

    # Kaynak dizin kontrolü
    print(f"Kaynak klasör kontrol ediliyor: {source_folder}")
    if not os.path.exists(source_folder):
        print(f"Hata: Yedekleme dizini bulunamadı: {source_folder}")
        return

    try:
        # Kaynak klasördeki dosyaları listele
        files_in_folder = sorted(os.listdir(source_folder), reverse=True)
        print(f"Kaynak klasördeki dosyalar: {files_in_folder}")

        if not files_in_folder:
            print(f"Yedekleme dosyası bulunamadı: {file_name}")
            return

        # En yeni dosyayı seç
        latest_file = files_in_folder[0]
        source_path = os.path.join(source_folder, latest_file)
        print(f"En yeni dosya: {source_path}")

        # Eski senkron dosyasını sil
        if os.path.exists(destination_path):
            os.remove(destination_path)
            print(f"Senkronizasyondan kaldırıldı: {file_name}")

        # Yeni dosyayı kopyala
        shutil.copy(source_path, destination_path)
        print(f"Senkronize edildi: {file_name}, Hedef: {destination_path}")

    except Exception as e:
        print(f"Senkronizasyon sırasında hata oluştu: {e}")

def auto_backup_and_sync(file_path):
    """Dosya yüklendiğinde veya düzenlendiğinde otomatik yedekleme ve senkronizasyon başlatır."""
    backup_file(file_path)
    sync_file(file_path)

class BackupAndSyncHandler(FileSystemEventHandler):
    
    def __init__(self, progress, total_files, callback):
        super().__init__()
        self.progress = progress
        self.total_files = total_files
        self.completed_files = 0
        self.callback = callback
        
    """Dosya değişikliklerini izleyen ve yedekleme/senkronizasyon yapan sınıf."""
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Değişiklik algılandı: {event.src_path}")
            auto_backup_and_sync(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"Yeni dosya algılandı: {event.src_path}")
            auto_backup_and_sync(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"Silinen dosya algılandı: {event.src_path}")
            file_name = os.path.basename(event.src_path)
            sync_path = os.path.join(SYNC_DIR, file_name)
            if os.path.exists(sync_path):
                os.remove(sync_path)
                print(f"{file_name} senkronizasyondan kaldırıldı.")
    
    def backup_file(self, file_path):
        """Dosyayı yedekleme işlemi"""
        dest_dir = "backup"
        os.makedirs(dest_dir, exist_ok=True)
        try:
            shutil.copy(file_path, dest_dir)
            self.completed_files += 1
            self.update_progress()
        except Exception as e:
            print(f"Dosya yedeklenemedi: {file_path}. Hata: {e}")

    def update_progress(self):
        progress_value = (self.completed_files / self.total_files) * 100
        self.progress['value'] = progress_value
        if self.completed_files >= self.total_files:
            self.callback()

def move_to_source(file_path):
    """Yüklenen dosyayı source dizinine taşır."""
    ensure_directories()
    if not os.path.isfile(file_path):
        print(f"{file_path} dosyası mevcut değil!")
        return

    # Dosyanın adını al
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(SOURCE_DIR, file_name)
    
def start_backup_and_sync(source_dir):
    """Verilen kaynak dizindeki dosyaları izler, yedekler ve senkronize eder."""
    ensure_directories()
    
    event_handler = BackupAndSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=True)
    observer.start()
    print(f"Yedekleme ve senkronizasyon başladı: {source_dir}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Yedekleme ve senkronizasyon durduruldu.")
    observer.join()

if __name__ == "__main__":
    ensure_directories()  # Gerekli dizinleri oluştur
    start_backup_and_sync(SOURCE_DIR)  # source dizinindeki dosyaları izleyerek yedekle ve senkronize et
