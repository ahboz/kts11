from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func, case
from datetime import datetime
import os
import pandas as pd
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kadro_takip.db'
db = SQLAlchemy(app)

# Birim modeli
class Birim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    bolumler = db.relationship('Bolum', back_populates='birim', lazy=True)
    ogretim_uyesi_sayilari = db.relationship('OgretimUyesiSayisi', backref='birim', lazy=True)
    kadro_talepleri = db.relationship('KadroTalebi', back_populates='birim')
    oncelikli_alanlar = db.relationship('OncelikliAlanArastirmaGorevlisi', back_populates='birim')
    kontenjan_tahsisleri = db.relationship('KontenjanTahsis', back_populates='birim')

# Bölüm modeli
class Bolum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    birim_id = db.Column(db.Integer, db.ForeignKey('birim.id'), nullable=False)
    birim = db.relationship('Birim', back_populates='bolumler')
    anabilim_dallari = db.relationship('AnabilimDali', back_populates='bolum')
    kadro_talepleri = db.relationship('KadroTalebi', back_populates='bolum')
    oncelikli_alanlar = db.relationship('OncelikliAlanArastirmaGorevlisi', back_populates='bolum')
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Anabilim Dalı modeli
class AnabilimDali(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    bolum_id = db.Column(db.Integer, db.ForeignKey('bolum.id'), nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    bolum = db.relationship('Bolum', back_populates='anabilim_dallari')
    kadro_talepleri = db.relationship('KadroTalebi', back_populates='anabilim_dali')
    oncelikli_alanlar = db.relationship('OncelikliAlanArastirmaGorevlisi', back_populates='anabilim_dali')

# Öğretim Üyesi Sayısı modeli
class OgretimUyesiSayisi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birim_id = db.Column(db.Integer, db.ForeignKey('birim.id'), nullable=False)
    ogretim_uyesi_sayisi = db.Column(db.Integer, default=0)
    arastirma_gorevlisi_sayisi = db.Column(db.Integer, default=0)
    ogretim_gorevlisi_sayisi = db.Column(db.Integer, default=0)
    oncelikli_alan_arastirma_gorevlisi_sayisi = db.Column(db.Integer, default=0)
    uykk_senato_ogretim_uyesi = db.Column(db.Integer, default=0)
    yok_onay_bekleyen_ogretim_uyesi = db.Column(db.Integer, default=0)
    yok_izin_alinan_ogretim_uyesi = db.Column(db.Integer, default=0)
    ilanda_ogretim_uyesi = db.Column(db.Integer, default=0)
    kurum_ici_atanan_ogretim_uyesi = db.Column(db.Integer, default=0)
    kurum_disi_atanan_ogretim_uyesi = db.Column(db.Integer, default=0)
    uykk_senato_arastirma_gorevlisi = db.Column(db.Integer, default=0)
    yok_onay_bekleyen_arastirma_gorevlisi = db.Column(db.Integer, default=0)
    yok_izin_alinan_arastirma_gorevlisi = db.Column(db.Integer, default=0)
    ilanda_arastirma_gorevlisi = db.Column(db.Integer, default=0)
    kurum_disi_atanan_arastirma_gorevlisi = db.Column(db.Integer, default=0)
    uykk_senato_ogretim_gorevlisi = db.Column(db.Integer, default=0)
    yok_onay_bekleyen_ogretim_gorevlisi = db.Column(db.Integer, default=0)
    yok_izin_alinan_ogretim_gorevlisi = db.Column(db.Integer, default=0)
    ilanda_ogretim_gorevlisi = db.Column(db.Integer, default=0)
    kurum_disi_atanan_ogretim_gorevlisi = db.Column(db.Integer, default=0)
    kalan_atama_kontenjani = db.Column(db.Integer, default=0)
    kalan_arastirma_gorevlisi_kontenjani = db.Column(db.Integer, default=0)
    kalan_ogretim_gorevlisi_kontenjani = db.Column(db.Integer, default=0)
    cari_yil_kontenjan = db.Column(db.Integer, default=0)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Kontenjan Tahsis modeli
class KontenjanTahsis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birim_id = db.Column(db.Integer, db.ForeignKey('birim.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    atama_kontenjani = db.Column(db.Integer, nullable=False, default=0)
    oncelikli_alan_arastirma_gorevlisi = db.Column(db.Integer, nullable=False, default=0)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    birim = db.relationship('Birim', back_populates='kontenjan_tahsisleri')

# Kadro Talebi modeli
class KadroTalebi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birim_id = db.Column(db.Integer, db.ForeignKey('birim.id'), nullable=False)
    bolum_id = db.Column(db.Integer, db.ForeignKey('bolum.id'), nullable=False)
    anabilim_dali_id = db.Column(db.Integer, db.ForeignKey('anabilim_dali.id'), nullable=False)
    unvan = db.Column(db.String(100), nullable=False)
    derece = db.Column(db.Integer, nullable=False)
    kadro_no = db.Column(db.Integer, nullable=False)
    kadro_turu = db.Column(db.String(100), nullable=False)
    norm_durumu = db.Column(db.String(50), nullable=False)
    islem_durumu = db.Column(db.String(100), nullable=False)
    yok_onay_durumu = db.Column(db.String(20))
    oncelikli_alan = db.Column(db.Boolean, default=False)
    ilan_tarihi = db.Column(db.Date)
    adi_soyadi = db.Column(db.String(100))
    # Yeni sütunlar
    fakulte_yonetim_kurulu_yazisi = db.Column(db.String(100))
    uyk_senato_talep_yazisi = db.Column(db.String(100))
    uyk_senato_onay_yazisi = db.Column(db.String(100))
    uyk_senato_karar_numarasi = db.Column(db.String(50))
    yok_kadro_talep_yazisi = db.Column(db.String(100))
    yoksis_form_no = db.Column(db.String(50))
    yok_izin_red_yazisi = db.Column(db.String(100))
    talep_tarihi = db.Column(db.DateTime, default=datetime.now)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    birim = db.relationship('Birim', back_populates='kadro_talepleri')
    bolum = db.relationship('Bolum', back_populates='kadro_talepleri')
    anabilim_dali = db.relationship('AnabilimDali', back_populates='kadro_talepleri')

# Öncelikli Alan Araştırma Görevlisi modeli
class OncelikliAlanArastirmaGorevlisi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    birim_id = db.Column(db.Integer, db.ForeignKey('birim.id'), nullable=False)
    bolum_id = db.Column(db.Integer, db.ForeignKey('bolum.id'), nullable=False)
    anabilim_dali_id = db.Column(db.Integer, db.ForeignKey('anabilim_dali.id'), nullable=False)
    kadro_sayisi = db.Column(db.Integer, default=0)
    aciklama = db.Column(db.Text)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.now)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    birim = db.relationship('Birim', back_populates='oncelikli_alanlar')
    bolum = db.relationship('Bolum', back_populates='oncelikli_alanlar')
    anabilim_dali = db.relationship('AnabilimDali', back_populates='oncelikli_alanlar')

# Sabit listeler
KADRO_TURLERI = [
    'Öğretim Üyesi',
    'Araştırma Görevlisi-Öğretim Görevlisi',
    'Öncelikli Alan Araştırma Görevlisi'
]

UNVANLAR = [
    'Profesör',
    'Doçent',
    'Doktor Öğretim Üyesi',
    'Öğretim Görevlisi',
    'Araştırma Görevlisi',
    'Araştırma Görevlisi(Öncelikli Alan)'
]

NORM_DURUMLARI = [
    'Norm İçi',
    'Asgari Aşan',
    'Norm Dışı'
]

ISLEM_DURUMLARI = [
    'ÜYKK/Senato Aşamasında',
    'YÖK\'ten Onay Bekliyor',
    'YÖK\'ten İzin Alındı İlan Edilebilir',
    'İlanda',
    'Kurum İçinden Atanan',
    'Kurum Dışından Atanan',
    'Kurum Dışından Atanan Doktor Öğretim Üyesi (35. Madde Uyarınca Bizde Eğitim Gören)'
]

YOK_ONAY_DURUMLARI = [
    'Evet',
    'Red',
    ''  # Boş seçenek
]

# Ana sayfa
@app.route('/')
def index():
    # Araştırma-Öğretim Görevlisi kontenjanı
    arastirma_ogretim_gorevlisi_query = db.session.query(
        func.sum(OgretimUyesiSayisi.kalan_arastirma_gorevlisi_kontenjani + OgretimUyesiSayisi.kalan_ogretim_gorevlisi_kontenjani)
    ).scalar() or 0

    # Öncelikli Alan Araştırma Görevlisi kontenjanı toplamı
    birimler = Birim.query.order_by(Birim.id).all()
    oncelikli_alan_kontenjani = 0
    for birim in birimler:
        ogretim_uyesi_sayisi = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).first()
        if ogretim_uyesi_sayisi:
            oncelikli_alan_kontenjani += ogretim_uyesi_sayisi.oncelikli_alan_arastirma_gorevlisi_sayisi if ogretim_uyesi_sayisi else 0

    # Öğretim Üyesi kontenjanı toplamı (Özet Çizelge tablosundan)
    ogretim_uyesi_kontenjani = db.session.query(
        func.sum(OgretimUyesiSayisi.ogretim_uyesi_sayisi)
    ).scalar() or 0

    # YÖK'ün reddettiği kadro talebi sayısı
    yok_red_sayisi = KadroTalebi.query.filter_by(yok_onay_durumu='Red').count()

    # İşlem durumlarını say (Sadece YÖK Red olanları hariç tut, boş olanları dahil et)
    islem_durumlari = db.session.query(
        KadroTalebi.islem_durumu,
        func.count(KadroTalebi.id).label('count')
    ).filter(
        or_(
            KadroTalebi.yok_onay_durumu != 'Red',
            KadroTalebi.yok_onay_durumu == None,
            KadroTalebi.yok_onay_durumu == ''
        )
    ).group_by(
        KadroTalebi.islem_durumu
    ).all()

    # İşlem durumlarını sözlüğe çevir
    islem_durumlari_dict = {
        'labels': [durum[0] for durum in islem_durumlari],
        'data': [durum[1] for durum in islem_durumlari]
    }

    # Kontenjan bilgilerini birleştir
    kontenjan_tahsisleri = {
        'arastirma_ogretim_gorevlisi': arastirma_ogretim_gorevlisi_query,
        'oncelikli_alan': oncelikli_alan_kontenjani,
        'ogretim_uyesi': ogretim_uyesi_kontenjani,
        'yok_red': yok_red_sayisi
    }

    return render_template('index.html',
                         kontenjan_tahsisleri=kontenjan_tahsisleri,
                         islem_durumlari=islem_durumlari_dict)

# Birimler sayfası ve işlemleri
@app.route('/birimler')
def birimler():
    birimler = Birim.query.order_by(Birim.id).all()
    return render_template('birimler.html', birimler=birimler)

@app.route('/birim/ekle', methods=['POST'])
def birim_ekle():
    ad = request.form.get('ad')
    if ad:
        try:
            yeni_birim = Birim(ad=ad)
            db.session.add(yeni_birim)
            db.session.commit()
            flash('Birim başarıyla eklendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Birim eklenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('birimler'))

@app.route('/birim_sil/<int:id>')
def birim_sil(id):
    try:
        birim = Birim.query.get(id)
        if birim:
            # Önce birime bağlı öğretim üyesi sayılarını sil
            OgretimUyesiSayisi.query.filter_by(birim_id=id).delete()
            
            # Birime bağlı bölümlerin anabilim dallarını sil
            for bolum in birim.bolumler:
                AnabilimDali.query.filter_by(bolum_id=bolum.id).delete()
            
            # Birime bağlı bölümleri sil
            Bolum.query.filter_by(birim_id=id).delete()
            
            # Birime bağlı kadro taleplerini sil
            KadroTalebi.query.filter_by(birim_id=id).delete()
            
            # En son birimi sil
            db.session.delete(birim)
            db.session.commit()
            flash('Birim başarıyla silindi.', 'success')
        else:
            flash('Birim bulunamadı.', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Birim silinirken bir hata oluştu.', 'error')
        print(f"Hata: {str(e)}")
    return redirect(url_for('birimler'))

@app.route('/birim/duzenle/<int:birim_id>', methods=['POST'])
def birim_duzenle(birim_id):
    birim = Birim.query.get_or_404(birim_id)
    ad = request.form.get('ad')
    if ad:
        try:
            birim.ad = ad
            db.session.commit()
            flash('Birim başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Birim güncellenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('birimler'))

# Bölümler sayfası
@app.route('/bolumler/<int:birim_id>')
def bolumler(birim_id):
    birim = Birim.query.get_or_404(birim_id)
    bolumler = Bolum.query.filter_by(birim_id=birim_id).all()
    return render_template('bolumler.html', birim=birim, bolumler=bolumler)

@app.route('/bolum/ekle/<int:birim_id>', methods=['POST'])
def bolum_ekle(birim_id):
    if request.method == 'POST':
        ad = request.form.get('ad')
        try:
            bolum = Bolum(ad=ad, birim_id=birim_id)
            db.session.add(bolum)
            db.session.commit()
            flash('Bölüm başarıyla eklendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Bölüm eklenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('bolumler', birim_id=birim_id))

@app.route('/bolum/duzenle/<int:bolum_id>', methods=['POST'])
def bolum_duzenle(bolum_id):
    bolum = Bolum.query.get_or_404(bolum_id)
    if request.method == 'POST':
        ad = request.form.get('ad')
        try:
            bolum.ad = ad
            db.session.commit()
            flash('Bölüm başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Bölüm güncellenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('bolumler', birim_id=bolum.birim_id))

@app.route('/bolum/sil/<int:bolum_id>', methods=['POST'])
def bolum_sil(bolum_id):
    bolum = Bolum.query.get_or_404(bolum_id)
    birim_id = bolum.birim_id
    try:
        db.session.delete(bolum)
        db.session.commit()
        flash('Bölüm başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Bölüm silinirken bir hata oluştu.', 'error')
        print(f"Hata: {str(e)}")
    return redirect(url_for('bolumler', birim_id=birim_id))

# Anabilim Dalları sayfası
@app.route('/anabilim-dallari/<int:bolum_id>')
def anabilim_dallari(bolum_id):
    bolum = Bolum.query.get_or_404(bolum_id)
    anabilim_dallari = AnabilimDali.query.filter_by(bolum_id=bolum_id).all()
    return render_template('anabilim_dallari.html', bolum=bolum, anabilim_dallari=anabilim_dallari)

@app.route('/anabilim-dali/ekle/<int:bolum_id>', methods=['POST'])
def anabilim_dali_ekle(bolum_id):
    if request.method == 'POST':
        ad = request.form.get('ad')
        try:
            anabilim_dali = AnabilimDali(ad=ad, bolum_id=bolum_id)
            db.session.add(anabilim_dali)
            db.session.commit()
            flash('Anabilim Dalı başarıyla eklendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Anabilim Dalı eklenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('anabilim_dallari', bolum_id=bolum_id))

@app.route('/anabilim-dali/duzenle/<int:anabilim_dali_id>', methods=['POST'])
def anabilim_dali_duzenle(anabilim_dali_id):
    anabilim_dali = AnabilimDali.query.get_or_404(anabilim_dali_id)
    if request.method == 'POST':
        ad = request.form.get('ad')
        try:
            anabilim_dali.ad = ad
            db.session.commit()
            flash('Anabilim Dalı başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Anabilim Dalı güncellenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")
    return redirect(url_for('anabilim_dallari', bolum_id=anabilim_dali.bolum_id))

@app.route('/anabilim-dali/sil/<int:anabilim_dali_id>', methods=['POST'])
def anabilim_dali_sil(anabilim_dali_id):
    anabilim_dali = AnabilimDali.query.get_or_404(anabilim_dali_id)
    bolum_id = anabilim_dali.bolum_id
    try:
        db.session.delete(anabilim_dali)
        db.session.commit()
        flash('Anabilim Dalı başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Anabilim Dalı silinirken bir hata oluştu.', 'error')
        print(f"Hata: {str(e)}")
    return redirect(url_for('anabilim_dallari', bolum_id=bolum_id))

# Kadro Talebi sayfası ve işlemleri
@app.route('/kadro-talebi')
def kadro_talebi():
    birimler = Birim.query.all()
    kadro_talepleri = KadroTalebi.query.order_by(KadroTalebi.id.desc()).all()
    return render_template('kadro_talebi.html', hide_footer=True, birimler=birimler, kadro_talepleri=kadro_talepleri, 
                         unvanlar=UNVANLAR, norm_durumlari=NORM_DURUMLARI, islem_durumlari=ISLEM_DURUMLARI, yok_onay_durumlari=YOK_ONAY_DURUMLARI, kadro_turleri=KADRO_TURLERI)

@app.route('/kadro-talebi/ekle', methods=['POST'])
def kadro_talebi_ekle():
    try:
        ilan_tarihi = None
        if request.form.get('ilan_tarihi'):
            ilan_tarihi = datetime.strptime(request.form['ilan_tarihi'], '%Y-%m-%d').date()
            
        yeni_talep = KadroTalebi(
            birim_id=request.form['birim_id'],
            bolum_id=request.form['bolum_id'],
            anabilim_dali_id=request.form['anabilim_dali_id'],
            unvan=request.form['unvan'],
            derece=request.form['derece'],
            kadro_no=request.form['kadro_no'],
            kadro_turu=request.form['kadro_turu'],
            norm_durumu=request.form['norm_durumu'],
            islem_durumu=request.form['islem_durumu'],
            yok_onay_durumu=request.form.get('yok_onay_durumu'),
            oncelikli_alan=request.form.get('oncelikli_alan'),
            ilan_tarihi=ilan_tarihi,
            adi_soyadi=request.form.get('adi_soyadi'),
            fakulte_yonetim_kurulu_yazisi=request.form.get('fakulte_yonetim_kurulu_yazisi'),
            uyk_senato_talep_yazisi=request.form.get('uyk_senato_talep_yazisi'),
            uyk_senato_onay_yazisi=request.form.get('uyk_senato_onay_yazisi'),
            uyk_senato_karar_numarasi=request.form.get('uyk_senato_karar_numarasi'),
            yok_kadro_talep_yazisi=request.form.get('yok_kadro_talep_yazisi'),
            yoksis_form_no=request.form.get('yoksis_form_no'),
            yok_izin_red_yazisi=request.form.get('yok_izin_red_yazisi')
        )
        db.session.add(yeni_talep)
        db.session.commit()
        flash('Kadro talebi başarıyla eklendi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Kadro talebi eklenirken bir hata oluştu.', 'danger')
        print(str(e))
    return redirect(url_for('kadro_talebi'))

@app.route('/kadro-talebi/duzenle/<int:talep_id>', methods=['GET', 'POST'])
def kadro_talebi_duzenle(talep_id):
    talep = KadroTalebi.query.get_or_404(talep_id)
    birimler = Birim.query.all()
    
    # Mevcut birimin bölümlerini al
    bolumler = Bolum.query.filter_by(birim_id=talep.birim_id).all()
    
    # Mevcut bölümün anabilim dallarını al
    anabilim_dallari = AnabilimDali.query.filter_by(bolum_id=talep.bolum_id).all()

    if request.method == 'POST':
        try:
            ilan_tarihi = None
            if request.form.get('ilan_tarihi'):
                ilan_tarihi = datetime.strptime(request.form['ilan_tarihi'], '%Y-%m-%d').date()
            
            talep.birim_id = request.form.get('birim_id')
            talep.bolum_id = request.form.get('bolum_id')
            talep.anabilim_dali_id = request.form.get('anabilim_dali_id')
            talep.unvan = request.form.get('unvan')
            talep.derece = request.form.get('derece')
            talep.kadro_no = request.form.get('kadro_no')
            talep.kadro_turu = request.form.get('kadro_turu')
            talep.norm_durumu = request.form.get('norm_durumu')
            talep.islem_durumu = request.form.get('islem_durumu')
            talep.yok_onay_durumu = request.form.get('yok_onay_durumu')
            talep.oncelikli_alan = request.form.get('oncelikli_alan')
            talep.ilan_tarihi = ilan_tarihi
            talep.adi_soyadi = request.form.get('adi_soyadi')
            talep.fakulte_yonetim_kurulu_yazisi = request.form.get('fakulte_yonetim_kurulu_yazisi')
            talep.uyk_senato_talep_yazisi = request.form.get('uyk_senato_talep_yazisi')
            talep.uyk_senato_onay_yazisi = request.form.get('uyk_senato_onay_yazisi')
            talep.uyk_senato_karar_numarasi = request.form.get('uyk_senato_karar_numarasi')
            talep.yok_kadro_talep_yazisi = request.form.get('yok_kadro_talep_yazisi')
            talep.yoksis_form_no = request.form.get('yoksis_form_no')
            talep.yok_izin_red_yazisi = request.form.get('yok_izin_red_yazisi')
            talep.guncelleme_tarihi = datetime.now()
            
            db.session.commit()

            # Özet çizelge sayılarını güncelle
            birim = Birim.query.get(talep.birim_id)
            if birim:
                ogretim_uyesi_sayisi = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).first()
                if not ogretim_uyesi_sayisi:
                    ogretim_uyesi_sayisi = OgretimUyesiSayisi(birim_id=birim.id)
                    db.session.add(ogretim_uyesi_sayisi)

                # Araştırma Görevlisi ve Öğretim Görevlisi sayılarını hesapla
                kadro_talepleri = KadroTalebi.query.filter_by(birim_id=birim.id).all()
                
                # Sayaçları sıfırla
                uykk_senato_arastirma = 0
                yok_onay_bekleyen_arastirma = 0
                yok_izin_alinan_arastirma = 0
                ilanda_arastirma = 0
                kurum_disi_atanan_arastirma = 0

                uykk_senato_ogretim = 0
                yok_onay_bekleyen_ogretim = 0
                yok_izin_alinan_ogretim = 0
                ilanda_ogretim = 0
                kurum_disi_atanan_ogretim = 0

                uykk_senato_ogretim_uyesi = 0
                yok_onay_bekleyen_ogretim_uyesi = 0
                yok_izin_alinan_ogretim_uyesi = 0
                ilanda_ogretim_uyesi = 0
                kurum_ici_atanan_ogretim_uyesi = 0
                kurum_disi_atanan_ogretim_uyesi = 0

                # Her kadro talebi için
                for talep in kadro_talepleri:
                    # Sadece "Araştırma Görevlisi-Öğretim Görevlisi" kadro türündeki ve YÖK onay durumu "Red" olmayanları say
                    if talep.kadro_turu == "Araştırma Görevlisi-Öğretim Görevlisi" and talep.yok_onay_durumu != "Red":
                        if talep.unvan == "Araştırma Görevlisi":
                            # Araştırma Görevlisi için işlem durumlarını say
                            if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                                uykk_senato_arastirma += 1
                            elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                                yok_onay_bekleyen_arastirma += 1
                            elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                                yok_izin_alinan_arastirma += 1
                            elif talep.islem_durumu == "İlanda":
                                ilanda_arastirma += 1
                            elif talep.islem_durumu == "Kurum Dışından Atanan":
                                kurum_disi_atanan_arastirma += 1
                        elif talep.unvan == "Öğretim Görevlisi":
                            # Öğretim Görevlisi için işlem durumlarını say
                            if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                                uykk_senato_ogretim += 1
                            elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                                yok_onay_bekleyen_ogretim += 1
                            elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                                yok_izin_alinan_ogretim += 1
                            elif talep.islem_durumu == "İlanda":
                                ilanda_ogretim += 1
                            elif talep.islem_durumu == "Kurum Dışından Atanan":
                                kurum_disi_atanan_ogretim += 1

                    # Öğretim Üyesi kadro türündeki ve YÖK onay durumu "Red" olmayanları say
                    if talep.kadro_turu == "Öğretim Üyesi" and talep.yok_onay_durumu != "Red":
                        if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                            uykk_senato_ogretim_uyesi += 1
                        elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                            yok_onay_bekleyen_ogretim_uyesi += 1
                        elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                            yok_izin_alinan_ogretim_uyesi += 1
                        elif talep.islem_durumu == "İlanda":
                            ilanda_ogretim_uyesi += 1
                        elif talep.islem_durumu == "Kurum İçinden Atanan":
                            kurum_ici_atanan_ogretim_uyesi += 1
                        elif talep.islem_durumu == "Kurum Dışından Atanan":
                            kurum_disi_atanan_ogretim_uyesi += 1

                # Sayıları OgretimUyesiSayisi modeline kaydet
                ogretim_uyesi_sayisi = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).first()
                if not ogretim_uyesi_sayisi:
                    ogretim_uyesi_sayisi = OgretimUyesiSayisi(birim_id=birim.id)
                    db.session.add(ogretim_uyesi_sayisi)

                # Araştırma Görevlisi sayılarını kaydet
                ogretim_uyesi_sayisi.uykk_senato_arastirma_gorevlisi = uykk_senato_arastirma
                ogretim_uyesi_sayisi.yok_onay_bekleyen_arastirma_gorevlisi = yok_onay_bekleyen_arastirma
                ogretim_uyesi_sayisi.yok_izin_alinan_arastirma_gorevlisi = yok_izin_alinan_arastirma
                ogretim_uyesi_sayisi.ilanda_arastirma_gorevlisi = ilanda_arastirma
                ogretim_uyesi_sayisi.kurum_disi_atanan_arastirma_gorevlisi = kurum_disi_atanan_arastirma

                # Öğretim Görevlisi sayılarını kaydet
                ogretim_uyesi_sayisi.uykk_senato_ogretim_gorevlisi = uykk_senato_ogretim
                ogretim_uyesi_sayisi.yok_onay_bekleyen_ogretim_gorevlisi = yok_onay_bekleyen_ogretim
                ogretim_uyesi_sayisi.yok_izin_alinan_ogretim_gorevlisi = yok_izin_alinan_ogretim
                ogretim_uyesi_sayisi.ilanda_ogretim_gorevlisi = ilanda_ogretim
                ogretim_uyesi_sayisi.kurum_disi_atanan_ogretim_gorevlisi = kurum_disi_atanan_ogretim

                # Öğretim Üyesi sayılarını kaydet
                ogretim_uyesi_sayisi.uykk_senato_ogretim_uyesi = uykk_senato_ogretim_uyesi
                ogretim_uyesi_sayisi.yok_onay_bekleyen_ogretim_uyesi = yok_onay_bekleyen_ogretim_uyesi
                ogretim_uyesi_sayisi.yok_izin_alinan_ogretim_uyesi = yok_izin_alinan_ogretim_uyesi
                ogretim_uyesi_sayisi.ilanda_ogretim_uyesi = ilanda_ogretim_uyesi
                ogretim_uyesi_sayisi.kurum_ici_atanan_ogretim_uyesi = kurum_ici_atanan_ogretim_uyesi
                ogretim_uyesi_sayisi.kurum_disi_atanan_ogretim_uyesi = kurum_disi_atanan_ogretim_uyesi

                # Araştırma Görevlisi için Kalan Kontenjan hesapla
                arastirma_gorevlisi_kontenjani = ogretim_uyesi_sayisi.arastirma_gorevlisi_sayisi or 0
                toplam_surecte_arastirma = (
                    uykk_senato_arastirma +  # ÜYKK/Senato Aşamasında
                    yok_onay_bekleyen_arastirma +  # YÖK'ten Onay Bekliyor
                    yok_izin_alinan_arastirma +  # YÖK'ten İzin Alındı
                    ilanda_arastirma +  # İlanda
                    kurum_disi_atanan_arastirma  # Kurum Dışından Atanan
                )
                ogretim_uyesi_sayisi.kalan_arastirma_gorevlisi_kontenjani = arastirma_gorevlisi_kontenjani - toplam_surecte_arastirma

                # Öğretim Görevlisi için Kalan Kontenjan hesapla
                ogretim_gorevlisi_kontenjani = ogretim_uyesi_sayisi.ogretim_gorevlisi_sayisi or 0
                toplam_surecte_ogretim = (
                    uykk_senato_ogretim +  # ÜYKK/Senato Aşamasında
                    yok_onay_bekleyen_ogretim +  # YÖK'ten Onay Bekliyor
                    yok_izin_alinan_ogretim +  # YÖK'ten İzin Alındı
                    ilanda_ogretim +  # İlanda
                    kurum_disi_atanan_ogretim  # Kurum Dışından Atanan
                )
                ogretim_uyesi_sayisi.kalan_ogretim_gorevlisi_kontenjani = ogretim_gorevlisi_kontenjani - toplam_surecte_ogretim

                # Öğretim Üyesi için Kalan Kontenjan hesapla
                ogretim_uyesi_kontenjani = ogretim_uyesi_sayisi.ogretim_uyesi_sayisi or 0
                toplam_surecte_ogretim_uyesi = (
                    uykk_senato_ogretim_uyesi +  # ÜYKK/Senato Aşamasında
                    yok_onay_bekleyen_ogretim_uyesi +  # YÖK'ten Onay Bekliyor
                    yok_izin_alinan_ogretim_uyesi +  # YÖK'ten İzin Alındı
                    ilanda_ogretim_uyesi +  # İlanda
                    kurum_disi_atanan_ogretim_uyesi  # Kurum Dışından Atanan
                )
                ogretim_uyesi_sayisi.kalan_atama_kontenjani = ogretim_uyesi_kontenjani - toplam_surecte_ogretim_uyesi

                db.session.commit()

            flash('Kadro talebi başarıyla güncellendi.', 'success')
            return redirect(url_for('kadro_talebi'))
        except Exception as e:
            db.session.rollback()
            flash('Kadro talebi güncellenirken bir hata oluştu.', 'error')
            print(f"Hata: {str(e)}")

    return render_template('kadro_talebi_duzenle.html', hide_footer=True, talep=talep, birimler=birimler, bolumler=bolumler, anabilim_dallari=anabilim_dallari, 
                         unvanlar=UNVANLAR, norm_durumlari=NORM_DURUMLARI, islem_durumlari=ISLEM_DURUMLARI, yok_onay_durumlari=YOK_ONAY_DURUMLARI, kadro_turleri=KADRO_TURLERI)

@app.route('/get-bolumler/<int:birim_id>')
def get_bolumler(birim_id):
    bolumler = Bolum.query.filter_by(birim_id=birim_id).all()
    return jsonify([{'id': bolum.id, 'ad': bolum.ad} for bolum in bolumler])

@app.route('/get-anabilim-dallari/<int:bolum_id>')
def get_anabilim_dallari(bolum_id):
    anabilim_dallari = AnabilimDali.query.filter_by(bolum_id=bolum_id).all()
    return jsonify([{'id': anabilim.id, 'ad': anabilim.ad} for anabilim in anabilim_dallari])

@app.route('/kadro-talebi/sil/<int:talep_id>', methods=['POST'])
def kadro_talebi_sil(talep_id):
    talep = KadroTalebi.query.get_or_404(talep_id)
    try:
        db.session.delete(talep)
        db.session.commit()
        flash('Kadro talebi başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Kadro talebi silinirken bir hata oluştu.', 'error')
        print(f"Hata: {str(e)}")
    return redirect(url_for('kadro_talebi'))

@app.route('/kadro-talepleri-excel')
def kadro_talepleri_excel():
    kadro_talepleri = KadroTalebi.query.order_by(KadroTalebi.id.desc()).all()
    
    # Excel için veri hazırlama
    data = []
    for talep in kadro_talepleri:
        data.append({
            'ID': talep.id,
            'Birim': talep.birim.ad,
            'Bölüm': talep.bolum.ad,
            'Anabilim Dalı': talep.anabilim_dali.ad,
            'Unvan': talep.unvan,
            'Derece': talep.derece,
            'Kadro No': talep.kadro_no,
            'Kadro Türü': talep.kadro_turu,
            'Norm Durumu': talep.norm_durumu,
            'İşlem Durumu': talep.islem_durumu,
            'Fakülte Y.K. Yazısı': talep.fakulte_yonetim_kurulu_yazisi,
            'ÜYK/Senato Talep Yazısı': talep.uyk_senato_talep_yazisi,
            'ÜYK/Senato Onay Yazısı': talep.uyk_senato_onay_yazisi,
            'ÜYK/Senato Karar Numarası': talep.uyk_senato_karar_numarasi,
            'YÖK Kadro Talep Yazısı': talep.yok_kadro_talep_yazisi,
            'YÖKSİS Form No': talep.yoksis_form_no,
            'YÖK İzin/Red Yazısı': talep.yok_izin_red_yazisi,
            'YÖK Onay Durumu': talep.yok_onay_durumu,
            'İlan Tarihi': talep.ilan_tarihi.strftime('%d.%m.%Y') if talep.ilan_tarihi else '',
            'Adı Soyadı': talep.adi_soyadi,
            'Öncelikli Alan': 'Evet' if talep.oncelikli_alan else 'Hayır'
        })
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # Excel dosyası oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Kadro Talepleri')
        worksheet = writer.sheets['Kadro Talepleri']
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'kadro_talepleri_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

# Özet Çizelge sayfası ve işlemleri
@app.route('/ozet-cizelge')
def ozet_cizelge():
    birimler = Birim.query.all()
    
    # Her birim için Öncelikli Alan kontenjanlarını al
    for birim in birimler:
        tahsis = KontenjanTahsis.query.filter_by(
            birim_id=birim.id, 
            yil=datetime.now().year
        ).first()
        
        # Öncelikli Alan kontenjanını birim nesnesine ekle
        birim.oncelikli_alan_kontenjani = tahsis.oncelikli_alan_arastirma_gorevlisi if tahsis else 0
        
        # Öncelikli alan kadro taleplerini al
        oncelikli_talepler = KadroTalebi.query.filter_by(
            birim_id=birim.id,
            oncelikli_alan=True
        ).all()
        
        # Her aşama için sayaçları sıfırla
        birim.oncelikli_uykk_senato = 0
        birim.oncelikli_yok_onay = 0
        birim.oncelikli_yok_izin = 0
        birim.oncelikli_ilanda = 0
        
        # Her talep için duruma göre sayıları artır
        for talep in oncelikli_talepler:
            # YÖK onay durumu Red ise sayma
            if talep.yok_onay_durumu == 'Red':
                continue
                
            if talep.islem_durumu == 'ÜYKK/Senato Aşamasında':
                birim.oncelikli_uykk_senato += 1
            elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                birim.oncelikli_yok_onay += 1
            elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                birim.oncelikli_yok_izin += 1
            elif talep.islem_durumu == 'İlanda':
                birim.oncelikli_ilanda += 1
    
    # Her birim için işlem durumlarına göre sayıları hesapla
    for birim in birimler:
        # Araştırma Görevlisi ve Öğretim Görevlisi sayılarını hesapla
        kadro_talepleri = KadroTalebi.query.filter_by(birim_id=birim.id).all()
        
        # Sayaçları sıfırla
        uykk_senato_arastirma = 0
        yok_onay_bekleyen_arastirma = 0
        yok_izin_alinan_arastirma = 0
        ilanda_arastirma = 0
        kurum_disi_atanan_arastirma = 0

        uykk_senato_ogretim = 0
        yok_onay_bekleyen_ogretim = 0
        yok_izin_alinan_ogretim = 0
        ilanda_ogretim = 0
        kurum_disi_atanan_ogretim = 0

        uykk_senato_ogretim_uyesi = 0
        yok_onay_bekleyen_ogretim_uyesi = 0
        yok_izin_alinan_ogretim_uyesi = 0
        ilanda_ogretim_uyesi = 0
        kurum_ici_atanan_ogretim_uyesi = 0
        kurum_disi_atanan_ogretim_uyesi = 0

        # Her kadro talebi için
        for talep in kadro_talepleri:
            # Sadece "Araştırma Görevlisi-Öğretim Görevlisi" kadro türündeki ve YÖK onay durumu "Red" olmayanları say
            if talep.kadro_turu == "Araştırma Görevlisi-Öğretim Görevlisi" and talep.yok_onay_durumu != "Red":
                if talep.unvan == "Araştırma Görevlisi":
                    # Araştırma Görevlisi için işlem durumlarını say
                    if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                        uykk_senato_arastirma += 1
                    elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                        yok_onay_bekleyen_arastirma += 1
                    elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                        yok_izin_alinan_arastirma += 1
                    elif talep.islem_durumu == "İlanda":
                        ilanda_arastirma += 1
                    elif talep.islem_durumu == "Kurum Dışından Atanan":
                        kurum_disi_atanan_arastirma += 1
                elif talep.unvan == "Öğretim Görevlisi":
                    # Öğretim Görevlisi için işlem durumlarını say
                    if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                        uykk_senato_ogretim += 1
                    elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                        yok_onay_bekleyen_ogretim += 1
                    elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                        yok_izin_alinan_ogretim += 1
                    elif talep.islem_durumu == "İlanda":
                        ilanda_ogretim += 1
                    elif talep.islem_durumu == "Kurum Dışından Atanan":
                        kurum_disi_atanan_ogretim += 1

            # Öğretim Üyesi kadro türündeki ve YÖK onay durumu "Red" olmayanları say
            if talep.kadro_turu == "Öğretim Üyesi" and talep.yok_onay_durumu != "Red":
                if talep.islem_durumu == "ÜYKK/Senato Aşamasında":
                    uykk_senato_ogretim_uyesi += 1
                elif talep.islem_durumu == "YÖK'ten Onay Bekliyor":
                    yok_onay_bekleyen_ogretim_uyesi += 1
                elif talep.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir":
                    yok_izin_alinan_ogretim_uyesi += 1
                elif talep.islem_durumu == "İlanda":
                    ilanda_ogretim_uyesi += 1
                elif talep.islem_durumu == "Kurum İçinden Atanan":
                    kurum_ici_atanan_ogretim_uyesi += 1
                elif talep.islem_durumu == "Kurum Dışından Atanan":
                    kurum_disi_atanan_ogretim_uyesi += 1

        # Sayıları OgretimUyesiSayisi modeline kaydet
        ogretim_uyesi_sayisi = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).first()
        if not ogretim_uyesi_sayisi:
            ogretim_uyesi_sayisi = OgretimUyesiSayisi(birim_id=birim.id)
            db.session.add(ogretim_uyesi_sayisi)

        # Araştırma Görevlisi sayılarını kaydet
        ogretim_uyesi_sayisi.uykk_senato_arastirma_gorevlisi = uykk_senato_arastirma
        ogretim_uyesi_sayisi.yok_onay_bekleyen_arastirma_gorevlisi = yok_onay_bekleyen_arastirma
        ogretim_uyesi_sayisi.yok_izin_alinan_arastirma_gorevlisi = yok_izin_alinan_arastirma
        ogretim_uyesi_sayisi.ilanda_arastirma_gorevlisi = ilanda_arastirma
        ogretim_uyesi_sayisi.kurum_disi_atanan_arastirma_gorevlisi = kurum_disi_atanan_arastirma

        # Öğretim Görevlisi sayılarını kaydet
        ogretim_uyesi_sayisi.uykk_senato_ogretim_gorevlisi = uykk_senato_ogretim
        ogretim_uyesi_sayisi.yok_onay_bekleyen_ogretim_gorevlisi = yok_onay_bekleyen_ogretim
        ogretim_uyesi_sayisi.yok_izin_alinan_ogretim_gorevlisi = yok_izin_alinan_ogretim
        ogretim_uyesi_sayisi.ilanda_ogretim_gorevlisi = ilanda_ogretim
        ogretim_uyesi_sayisi.kurum_disi_atanan_ogretim_gorevlisi = kurum_disi_atanan_ogretim

        # Öğretim Üyesi sayılarını kaydet
        ogretim_uyesi_sayisi.uykk_senato_ogretim_uyesi = uykk_senato_ogretim_uyesi
        ogretim_uyesi_sayisi.yok_onay_bekleyen_ogretim_uyesi = yok_onay_bekleyen_ogretim_uyesi
        ogretim_uyesi_sayisi.yok_izin_alinan_ogretim_uyesi = yok_izin_alinan_ogretim_uyesi
        ogretim_uyesi_sayisi.ilanda_ogretim_uyesi = ilanda_ogretim_uyesi
        ogretim_uyesi_sayisi.kurum_ici_atanan_ogretim_uyesi = kurum_ici_atanan_ogretim_uyesi
        ogretim_uyesi_sayisi.kurum_disi_atanan_ogretim_uyesi = kurum_disi_atanan_ogretim_uyesi

        # Araştırma Görevlisi için Kalan Kontenjan hesapla
        arastirma_gorevlisi_kontenjani = ogretim_uyesi_sayisi.arastirma_gorevlisi_sayisi or 0
        toplam_surecte_arastirma = (
            uykk_senato_arastirma +  # ÜYKK/Senato Aşamasında
            yok_onay_bekleyen_arastirma +  # YÖK'ten Onay Bekliyor
            yok_izin_alinan_arastirma +  # YÖK'ten İzin Alındı
            ilanda_arastirma +  # İlanda
            kurum_disi_atanan_arastirma  # Kurum Dışından Atanan
        )
        ogretim_uyesi_sayisi.kalan_arastirma_gorevlisi_kontenjani = arastirma_gorevlisi_kontenjani - toplam_surecte_arastirma

        # Öğretim Görevlisi için Kalan Kontenjan hesapla
        ogretim_gorevlisi_kontenjani = ogretim_uyesi_sayisi.ogretim_gorevlisi_sayisi or 0
        toplam_surecte_ogretim = (
            uykk_senato_ogretim +  # ÜYKK/Senato Aşamasında
            yok_onay_bekleyen_ogretim +  # YÖK'ten Onay Bekliyor
            yok_izin_alinan_ogretim +  # YÖK'ten İzin Alındı
            ilanda_ogretim +  # İlanda
            kurum_disi_atanan_ogretim  # Kurum Dışından Atanan
        )
        ogretim_uyesi_sayisi.kalan_ogretim_gorevlisi_kontenjani = ogretim_gorevlisi_kontenjani - toplam_surecte_ogretim

        # Öğretim Üyesi için Kalan Kontenjan hesapla
        ogretim_uyesi_kontenjani = ogretim_uyesi_sayisi.ogretim_uyesi_sayisi or 0
        toplam_surecte_ogretim_uyesi = (
            uykk_senato_ogretim_uyesi +  # ÜYKK/Senato Aşamasında
            yok_onay_bekleyen_ogretim_uyesi +  # YÖK'ten Onay Bekliyor
            yok_izin_alinan_ogretim_uyesi +  # YÖK'ten İzin Alındı
            ilanda_ogretim_uyesi +  # İlanda
            kurum_disi_atanan_ogretim_uyesi  # Kurum Dışından Atanan
        )
        ogretim_uyesi_sayisi.kalan_atama_kontenjani = ogretim_uyesi_kontenjani - toplam_surecte_ogretim_uyesi

        db.session.commit()
    
    # Toplamları hesapla
    toplamlar = {
        'ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].ogretim_uyesi_sayisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'arastirma_gorevlisi': sum(birim.ogretim_uyesi_sayilari[0].arastirma_gorevlisi_sayisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'ogretim_gorevlisi': sum(birim.ogretim_uyesi_sayilari[0].ogretim_gorevlisi_sayisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'oncelikli_alan_arastirma_gorevlisi': sum(birim.ogretim_uyesi_sayilari[0].oncelikli_alan_arastirma_gorevlisi_sayisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        
        # Araştırma Görevlisi toplamları
        'uykk_senato_arastirma': sum(birim.ogretim_uyesi_sayilari[0].uykk_senato_arastirma_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_onay_bekleyen_arastirma': sum(birim.ogretim_uyesi_sayilari[0].yok_onay_bekleyen_arastirma_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_izin_alinan_arastirma': sum(birim.ogretim_uyesi_sayilari[0].yok_izin_alinan_arastirma_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'ilanda_arastirma': sum(birim.ogretim_uyesi_sayilari[0].ilanda_arastirma_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kurum_disi_atanan_arastirma': sum(birim.ogretim_uyesi_sayilari[0].kurum_disi_atanan_arastirma_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kalan_arastirma': sum(birim.ogretim_uyesi_sayilari[0].kalan_arastirma_gorevlisi_kontenjani or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        
        # Öğretim Görevlisi toplamları
        'uykk_senato_ogretim': sum(birim.ogretim_uyesi_sayilari[0].uykk_senato_ogretim_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_onay_bekleyen_ogretim': sum(birim.ogretim_uyesi_sayilari[0].yok_onay_bekleyen_ogretim_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_izin_alinan_ogretim': sum(birim.ogretim_uyesi_sayilari[0].yok_izin_alinan_ogretim_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'ilanda_ogretim': sum(birim.ogretim_uyesi_sayilari[0].ilanda_ogretim_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kurum_disi_atanan_ogretim': sum(birim.ogretim_uyesi_sayilari[0].kurum_disi_atanan_ogretim_gorevlisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kalan_ogretim': sum(birim.ogretim_uyesi_sayilari[0].kalan_ogretim_gorevlisi_kontenjani or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        
        # Öğretim Üyesi toplamları
        'uykk_senato_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].uykk_senato_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_onay_bekleyen_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].yok_onay_bekleyen_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'yok_izin_alinan_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].yok_izin_alinan_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'ilanda_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].ilanda_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kurum_ici_atanan_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].kurum_ici_atanan_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        'kurum_disi_atanan_ogretim_uyesi': sum(birim.ogretim_uyesi_sayilari[0].kurum_disi_atanan_ogretim_uyesi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
        
        # Öncelikli Alan toplamları
        'oncelikli_alan_arastirma': sum(birim.ogretim_uyesi_sayilari[0].oncelikli_alan_arastirma_gorevlisi_sayisi or 0 if birim.ogretim_uyesi_sayilari else 0 for birim in birimler),
    }
    
    return render_template('ozet_cizelge.html', birimler=birimler, toplamlar=toplamlar)

@app.route('/guncelle_ogretim_uyesi_sayisi', methods=['POST'])
def guncelle_ogretim_uyesi_sayisi():
    try:
        data = request.get_json()
        birim_id = data.get('birim_id')
        field_type = data.get('field_type')
        new_value = data.get('new_value')

        kayit = OgretimUyesiSayisi.query.filter_by(birim_id=birim_id).first()
        if not kayit:
            kayit = OgretimUyesiSayisi(birim_id=birim_id)
            db.session.add(kayit)

        if field_type == 'ogretim_uyesi':
            kayit.ogretim_uyesi_sayisi = new_value
        elif field_type == 'arastirma_gorevlisi':
            kayit.arastirma_gorevlisi_sayisi = new_value
        elif field_type == 'ogretim_gorevlisi':
            kayit.ogretim_gorevlisi_sayisi = new_value
        elif field_type == 'oncelikli_alan_arastirma_gorevlisi':
            kayit.oncelikli_alan_arastirma_gorevlisi_sayisi = new_value

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Öncelikli Alan Araştırma Görevlisi sayfası
@app.route('/oncelikli-alan-arastirma-gorevlisi')
def oncelikli_alan_arastirma_gorevlisi():
    # Birimleri ID'ye göre sırala
    birimler = Birim.query.order_by(Birim.id).all()
    
    # Her birim için kontenjan bilgisini al
    kontenjanlar = {}
    uykk_senato_sayilari = {}
    yok_onay_bekleyen_sayilari = {}
    yok_izin_alinan_sayilari = {}
    ilanda_sayilari = {}
    atanan_sayilari = {}
    kalan_kontenjan_sayilari = {}
    
    for birim in birimler:
        # Kontenjan bilgisi
        ogretim_uyesi_sayisi = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).first()
        kontenjanlar[birim.id] = ogretim_uyesi_sayisi.oncelikli_alan_arastirma_gorevlisi_sayisi if ogretim_uyesi_sayisi else 0
        
        # YÖK onay durumu filtresi (boş veya "Evet" olanları say)
        yok_onay_filtresi = (KadroTalebi.yok_onay_durumu == None) | (KadroTalebi.yok_onay_durumu == '') | (KadroTalebi.yok_onay_durumu == 'Evet')
        
        # ÜYKK/Senato aşamasındaki kadroları say
        uykk_senato_sayisi = KadroTalebi.query.filter(
            KadroTalebi.birim_id == birim.id,
            KadroTalebi.islem_durumu == 'ÜYKK/Senato Aşamasında',
            KadroTalebi.kadro_turu == 'Öncelikli Alan Araştırma Görevlisi',
            yok_onay_filtresi
        ).count()
        
        # YÖK'ten Onay Bekleyen kadroları say
        yok_onay_bekleyen = KadroTalebi.query.filter(
            KadroTalebi.birim_id == birim.id,
            KadroTalebi.islem_durumu == "YÖK'ten Onay Bekliyor",
            KadroTalebi.kadro_turu == 'Öncelikli Alan Araştırma Görevlisi',
            yok_onay_filtresi
        ).count()
        
        # YÖK'ten İzin Alındı İlan Edilebilir kadroları say
        yok_izin_alinan = KadroTalebi.query.filter(
            KadroTalebi.birim_id == birim.id,
            KadroTalebi.islem_durumu == "YÖK'ten İzin Alındı İlan Edilebilir",
            KadroTalebi.kadro_turu == 'Öncelikli Alan Araştırma Görevlisi',
            yok_onay_filtresi
        ).count()
        
        # İlanda olan kadroları say
        ilanda = KadroTalebi.query.filter(
            KadroTalebi.birim_id == birim.id,
            KadroTalebi.islem_durumu == 'İlanda',
            KadroTalebi.kadro_turu == 'Öncelikli Alan Araştırma Görevlisi',
            yok_onay_filtresi
        ).count()
        
        # Kurum Dışından Atanan kadroları say
        atanan = KadroTalebi.query.filter(
            KadroTalebi.birim_id == birim.id,
            KadroTalebi.islem_durumu == 'Kurum Dışından Atanan',
            KadroTalebi.kadro_turu == 'Öncelikli Alan Araştırma Görevlisi',
            yok_onay_filtresi
        ).count()
        
        uykk_senato_sayilari[birim.id] = uykk_senato_sayisi
        yok_onay_bekleyen_sayilari[birim.id] = yok_onay_bekleyen
        yok_izin_alinan_sayilari[birim.id] = yok_izin_alinan
        ilanda_sayilari[birim.id] = ilanda
        atanan_sayilari[birim.id] = atanan
        
        # Kalan kontenjan hesapla
        toplam_kullanilan = (uykk_senato_sayisi + 
                           yok_onay_bekleyen + 
                           yok_izin_alinan + 
                           ilanda + 
                           atanan)
        kalan_kontenjan_sayilari[birim.id] = kontenjanlar[birim.id] - toplam_kullanilan
    
    return render_template('oncelikli_alan_arastirma_gorevlisi.html', 
                         birimler=birimler, 
                         kontenjanlar=kontenjanlar,
                         uykk_senato_sayilari=uykk_senato_sayilari,
                         yok_onay_bekleyen_sayilari=yok_onay_bekleyen_sayilari,
                         yok_izin_alinan_sayilari=yok_izin_alinan_sayilari,
                         ilanda_sayilari=ilanda_sayilari,
                         atanan_sayilari=atanan_sayilari,
                         kalan_kontenjan_sayilari=kalan_kontenjan_sayilari)

# Raporlar sayfası
@app.route('/raporlar')
def raporlar():
    birimler = Birim.query.all()
    return render_template('raporlar.html', birimler=birimler)

# Birim bazlı rapor
@app.route('/birim_raporu', methods=['GET', 'POST'])
def birim_raporu():
    birimler = Birim.query.all()
    selected_birim = None
    kadro_talepleri = []

    if request.method == 'POST':
        birim_id = request.form.get('birim_id')
        if birim_id:
            selected_birim = Birim.query.get(birim_id)
            kadro_talepleri = KadroTalebi.query.filter_by(birim_id=birim_id).all()

    return render_template('birim_raporu.html',
                         birimler=birimler,
                         selected_birim=selected_birim,
                         kadro_talepleri=kadro_talepleri,
                         datetime=datetime)

# Genel rapor
@app.route('/genel_rapor', methods=['GET', 'POST'])
def genel_rapor():
    # Tüm verileri al
    birimler = Birim.query.all()
    kadro_talepleri = KadroTalebi.query.all()
    kontenjan_tahsisleri = KontenjanTahsis.query.all()
    
    # Her birim için öğretim üyesi sayılarını ve durumlarını al
    for birim in birimler:
        son_kayit = OgretimUyesiSayisi.query.filter_by(birim_id=birim.id).order_by(OgretimUyesiSayisi.guncelleme_tarihi.desc()).first()
        if son_kayit:
            birim.son_kayit = son_kayit
        else:
            birim.son_kayit = None
    
    # Kontenjan tahsis verilerini birim bazında topla
    birim_kontenjan = {}
    for tahsis in kontenjan_tahsisleri:
        if tahsis.birim_id not in birim_kontenjan:
            birim_kontenjan[tahsis.birim_id] = {
                'atama_kontenjani': 0,
                'atanan': 0,
                'oncelikli_alan': 0,
                'oncelikli_atanan': 0
            }
        birim_kontenjan[tahsis.birim_id]['atama_kontenjani'] += tahsis.atama_kontenjani
        birim_kontenjan[tahsis.birim_id]['oncelikli_alan'] += tahsis.oncelikli_alan_arastirma_gorevlisi
    
    # Rapor HTML'ini oluştur
    rapor_html = render_template(
        'genel_rapor.html',
        birimler=birimler,
        kadro_talepleri=kadro_talepleri,
        kontenjan_tahsisleri=kontenjan_tahsisleri,
        birim_kontenjan=birim_kontenjan,
        datetime=datetime
    )
    
    if request.method == 'POST':
        # HTML dosyası olarak gönder
        response = make_response(rapor_html)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=genel_rapor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        return response
    
    return rapor_html

# Veritabanını oluştur
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Render'da çalışırken PORT ortam değişkenini kullan, yerel geliştirmede 3001 portunu kullan
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=False)
