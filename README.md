# Kadro Takip Sistemi

Bu proje, kadro takibi için geliştirilmiş bir Flask web uygulamasıdır.

## Özellikler

- Birim, bölüm ve anabilim dalı yönetimi
- Kadro talepleri takibi
- Öncelikli alan araştırma görevlisi takibi
- Çeşitli raporlama özellikleri

## Kurulum

1. Gereksinimleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Uygulamayı başlatın:
   ```
   flask run
   ```
   veya
   ```
   python app.py
   ```

## Render'a Deploy Etme

Bu proje Render platformunda kolayca deploy edilebilir:

1. [Render](https://render.com/) hesabı oluşturun
2. "New Web Service" seçeneğini tıklayın
3. GitHub veya GitLab hesabınızı bağlayın ve bu projeyi seçin
4. Aşağıdaki ayarları yapılandırın:
   - **Name**: kadro-takip-sistemi (veya istediğiniz bir isim)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. "Create Web Service" butonuna tıklayın

Render, render.yaml dosyasını otomatik olarak algılayacak ve gerekli yapılandırmaları uygulayacaktır.

## Veritabanı Yapılandırması

Render'da SQLite kullanmak yerine, PostgreSQL kullanmanız önerilir. Render'ın ücretsiz PostgreSQL hizmetini kullanabilirsiniz. Veritabanı bağlantısını güncellemek için app.py dosyasındaki veritabanı yapılandırmasını değiştirin.