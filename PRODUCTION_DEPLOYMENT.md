# 🚀 Production Deployment Guide

## Üretim Ortamına Geçiş Adımları

### 📋 Hazırlık (Tamamlandı ✅)

- [x] Supabase local development çalışıyor
- [x] Database schema hazır (record template architecture)
- [x] Migration dosyası oluşturuldu
- [x] Bug'lar düzeltildi (field persistence, modal positioning)
- [x] localStorage fallback çalışıyor

---

## 🌐 Adım 1: Production Supabase Projesi Oluştur

### 1.1 Supabase Dashboard'a Git

```bash
# Tarayıcıda aç
https://supabase.com/dashboard
```

### 1.2 Yeni Proje Oluştur

1. **"New Project"** butonuna tıkla
2. **Organization:** Mevcut organization seç veya yeni oluştur
3. **Project Name:** `canvas-app-production`
4. **Database Password:** Güçlü bir şifre oluştur (kaydet!)
5. **Region:** Türkiye'ye en yakın: `Europe (Frankfurt)` veya `Europe (London)`
6. **Pricing Plan:** Free tier ile başla (sonra Pro'ya yükselt)
7. **"Create New Project"** tıkla

⏱️ **Süre:** Proje 2-3 dakika içinde hazır olur.

---

## 🔑 Adım 2: API Credentials Al

### 2.1 Project Settings'e Git

Dashboard'da yeni projen açık iken:

```
Settings → API → Project API keys
```

### 2.2 Değerleri Kopyala

```bash
Project URL:  https://your-project-ref.supabase.co
anon (public) key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.3 .env Dosyasını Güncelle

```bash
cd /Users/ali/Documents/Projects/spidyaprototype/canvas-app

# .env dosyasını düzenle
nano .env
```

**.env içeriği:**
```bash
VITE_API_URL=http://localhost:3001

# Supabase Configuration - PRODUCTION
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Enable Supabase
VITE_ENABLE_SUPABASE=true
```

**⚠️ ÖNEMLİ:** `.env` dosyasını `.gitignore`'a ekle (zaten ekli).

---

## 🗄️ Adım 3: Database Schema'yı Uygula

### 3.1 Supabase SQL Editor'ü Aç

Dashboard'da:

```
SQL Editor → New query
```

### 3.2 Migration'ı Kopyala ve Çalıştır

```bash
# Migration dosyasını oku
cat /Users/ali/Documents/Projects/spidyaprototype/canvas-app/supabase/migrations/20260117140000_record_template_architecture.sql
```

**Veya direkt çalıştır:**

1. SQL Editor'de yeni query aç
2. Migration dosyasının içeriğini yapıştır
3. **"Run"** butonuna tıkla (Cmd+Enter)
4. Başarılı olduğunu doğrula

### 3.3 Tabloları Kontrol Et

Dashboard'da:

```
Table Editor → Tables listesi
```

**Görmen gereken tablolar:**
- record_templates
- template_fields
- records
- record_values
- forms_v2
- record_template_views
- record_relationships
- record_links

---

## 🧪 Adım 4: Connection Test Et

### 4.1 Local Development Server'ı Yeniden Başlat

```bash
cd /Users/ali/Documents/Projects/spidyaprototype/canvas-app

# Dev server'ı kapat (Ctrl+C) ve yeniden başlat
npm run dev
```

### 4.2 Tarayıcıda Aç

```
http://localhost:5173/design
```

### 4.3 Test Senaryosu

**✅ Template Oluştur:**
1. "Yeni Template" butonuna tıkla
2. Adı: "Test Production"
3. 2-3 field ekle (Email, Text, Phone)
4. "Save Changes" tıkla
5. **Beklenen:** Template card'da "3 alan" görmeli

**✅ Form Oluştur:**
1. Template dropdown → "Formlar (0)"
2. "New Form" tıkla
3. Tüm field'ları seç
4. "Create Form" tıkla
5. **Beklenen:** Form başarıyla kaydedilmeli

**✅ Supabase'de Kontrol Et:**
1. Supabase Dashboard → Table Editor
2. `record_templates` tablosuna bak
3. **Beklenen:** "Test Production" template'i görmeli
4. `template_fields` tablosuna bak
5. **Beklenen:** 3 field görmeli

---

## 🌍 Adım 5: Frontend Deploy (Vercel)

### 5.1 GitHub Repository Oluştur

```bash
cd /Users/ali/Documents/Projects/spidyaprototype/canvas-app

# Git başlat (eğer yoksa)
git init
git add .
git commit -m "Production ready: Record Template Architecture"

# GitHub'a push et
git remote add origin https://github.com/YOUR-USERNAME/canvas-app.git
git branch -M main
git push -u origin main
```

### 5.2 Vercel'de Deploy Et

1. **Vercel Dashboard'a git:** https://vercel.com
2. **"New Project"** tıkla
3. **Import Git Repository** → GitHub repo'nu seç
4. **Build Settings:**
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. **Environment Variables:** (ÖNEMLİ!)
   ```
   VITE_SUPABASE_URL = https://your-project-ref.supabase.co
   VITE_SUPABASE_ANON_KEY = eyJhbGciOi...
   VITE_ENABLE_SUPABASE = true
   ```
6. **"Deploy"** tıkla

⏱️ **Süre:** 2-3 dakika içinde deploy olur.

### 5.3 Production URL'i Al

Deploy tamamlanınca:

```
https://canvas-app-production.vercel.app
```

---

## 🔒 Adım 6: Güvenlik Ayarları (Opsiyonel)

### 6.1 CORS Ayarları

Supabase Dashboard:

```
Settings → API → CORS Configuration
```

**Allowed Origins'e ekle:**
```
https://canvas-app-production.vercel.app
http://localhost:5173
```

### 6.2 Row Level Security (İleride)

Şu anda tüm tablolarda `"Allow all for now"` policy var.

**Authentication eklenince:**
1. User-based policies oluştur
2. `user_id` kolonları ekle
3. JWT claims kullanarak filtering yap

---

## 📊 Adım 7: Monitoring & Logs

### 7.1 Supabase Logs

Dashboard:

```
Logs & Stats → API Logs
```

**Görebileceğin bilgiler:**
- API request count
- Error rates
- Response times
- Database queries

### 7.2 Vercel Analytics

Vercel Dashboard:

```
Project → Analytics
```

**Görebileceğin metrikler:**
- Page views
- Unique visitors
- Performance (Web Vitals)
- Error rates

---

## 🐛 Troubleshooting

### Problem 1: "Failed to fetch" Hatası

**Sebep:** CORS hatası veya Supabase credentials yanlış

**Çözüm:**
```bash
# 1. .env dosyasını kontrol et
cat .env

# 2. Browser console'u aç (F12)
# 3. Network tab'ında Supabase isteklerini kontrol et
# 4. CORS hatası görüyorsan → Supabase CORS settings'i güncelle
```

### Problem 2: "Row Level Security" Hatası

**Sebep:** RLS enabled ama policy yok

**Çözüm:**
```sql
-- Supabase SQL Editor'de çalıştır
ALTER TABLE record_templates DISABLE ROW LEVEL SECURITY;
ALTER TABLE template_fields DISABLE ROW LEVEL SECURITY;
-- (Diğer tablolar için de tekrarla)
```

### Problem 3: Migration Hatası

**Sebep:** Tablolar zaten var veya syntax error

**Çözüm:**
```sql
-- 1. Mevcut tabloları kontrol et
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 2. Eğer eski migration çalıştıysa, önce drop et
DROP TABLE IF EXISTS record_templates CASCADE;
-- (Diğer tablolar için de tekrarla)

-- 3. Migration'ı tekrar çalıştır
```

---

## ✅ Checklist: Deployment Tamamlandı mı?

- [ ] Supabase production projesi oluşturuldu
- [ ] API credentials alındı ve `.env` güncellendi
- [ ] Database migration uygulandı
- [ ] Local test başarılı (template + form oluşturma)
- [ ] Supabase Table Editor'de data görünüyor
- [ ] GitHub repo oluşturuldu ve push edildi
- [ ] Vercel'de deploy edildi
- [ ] Production URL açılıyor
- [ ] Production'da template oluşturma test edildi
- [ ] Supabase logs kontrol edildi

---

## 🎯 Sonraki Adımlar

### Phase 1: Stabilization (1 hafta)
- [ ] Production'da kapsamlı test
- [ ] Bug fix'ler (eğer varsa)
- [ ] Performance monitoring

### Phase 2: Authentication (1-2 hafta)
- [ ] Supabase Auth entegrasyonu
- [ ] User registration/login
- [ ] Row Level Security policies
- [ ] Multi-tenant architecture

### Phase 3: Advanced Features (2-4 hafta)
- [ ] Record relationships (1:N, N:N)
- [ ] Multi-view pages (tabs)
- [ ] Workflow designer
- [ ] File uploads (Supabase Storage)

---

## 📞 Destek

**Supabase Docs:**
- https://supabase.com/docs
- https://supabase.com/docs/guides/database

**Vercel Docs:**
- https://vercel.com/docs
- https://vercel.com/docs/deployments

**Canvas App Docs:**
- `CLAUDE.md` - Claude Code kullanımı için
- `RECORD_ARCHITECTURE_GUIDE.md` - Sistem mimarisi
- `IMPLEMENTATION_SUMMARY.md` - Uygulama detayları

---

**Son Güncelleme:** 2026-01-17
**Durum:** ✅ Production'a hazır
