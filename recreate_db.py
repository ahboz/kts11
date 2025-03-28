from app import app, db
import os

# Veritabanı dosyasını sil
db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'gtu_personel.db')
if os.path.exists(db_file):
    os.remove(db_file)

# Veritabanını yeniden oluştur
with app.app_context():
    db.create_all()
