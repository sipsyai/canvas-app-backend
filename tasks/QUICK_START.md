# 🚀 Backend Task Quick Start Guide

## Nasıl Kullanılır?

### Seçenek 1: Claude ile Otomatik Çalıştırma (ÖNERİLEN)

Her task dosyasının başında `🤖 CLAUDE PROMPT` bloğu var. Sadece kopyala-yapıştır:

```bash
# 1. Task dosyasını aç
cat tasks/priority-1-critical/01-field-model-schema-update.md

# 2. İlk bloktaki (🤖 CLAUDE PROMPT) kısmı Claude'a kopyala
# 3. Claude otomatik olarak tüm adımları uygular
```

### Seçenek 2: Manuel Adım Adım

```bash
# 1. Task dosyasını oku
cat tasks/priority-1-critical/01-field-model-schema-update.md

# 2. Implementation Steps bölümünü takip et
# 3. Her adımı uygula
# 4. Acceptance Criteria'yı kontrol et
```

---

## En Hızlı Yol (2 Gün - %90 Ready)

Sadece **Priority 1** task'larını yap:

```bash
# Day 1
Task 01: Field Model Schema Update     (2-3h)
Task 02: Object Model Schema Update    (1-2h)

# Day 2  
Task 05: System Fields Seed Data       (1h)
```

**Toplam:** 4-6 saat → Backend %90 hazır! ✅

---

## Task Dosya Formatı

Her task dosyası şu yapıda:

```markdown
# 🤖 CLAUDE PROMPT - Task XX
```
Claude'a verilebilecek hazır prompt
```

## 📋 Objective
Ne yapılacak

## 🎯 Problem  
Neden gerekli

## 📝 Implementation Steps
Adım adım kod örnekleri

## ✅ Acceptance Criteria
- [ ] Checklist 1
- [ ] Checklist 2

## 🧪 Testing
Test komutları

## 🚨 Rollback Plan
Hata durumunda ne yapılır
```

---

## Task Öncelikleri

### 🔴 Priority 1: CRITICAL (MUTLAKA YAPILMALI)
- Task 01: Field Model Schema Update
- Task 02: Object Model Schema Update  
- Task 05: System Fields Seed Data

### 🟡 Priority 2: IMPORTANT (ÖNEMLİ)
- Task 06: User Object Implementation
- Task 07: RLS Policies Verification

### 🟢 Priority 3: IMPROVEMENTS (İYİLEŞTİRME)
- Task 08: OpenAPI Docs
- Task 09: Error Handling
- Task 10: Logging

---

## Hızlı Komutlar

```bash
# Virtual env aktif et (HER ZAMAN!)
source venv/bin/activate

# Migration çalıştır
alembic upgrade head

# Migration geri al
alembic downgrade -1

# Test
pytest

# Database kontrol
psql $DATABASE_URL -c "\d fields"

# API başlat
uvicorn app.main:app --reload
```

---

## Sorun Giderme

### Migration Hatası
```bash
alembic downgrade -1
alembic upgrade head
```

### Test Hatası
```bash
pytest -v  # Detaylı output
pytest tests/test_fields.py -k test_name  # Tek test
```

### Database Hatası
```bash
psql $DATABASE_URL -c "SELECT * FROM fields LIMIT 5;"
```

---

**İlk adım:** `tasks/priority-1-critical/01-field-model-schema-update.md` dosyasını aç! 🚀
