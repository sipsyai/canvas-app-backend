# Backend Development Tasks

Bu klasör, Canvas App Backend projesinin geliştirilmesi için Claude Code'a verilecek task'ları içerir.

## 📋 Task Sırası

Task'lar **sırayla** yapılmalıdır. Her task bir öncekine bağımlıdır.

| Task | Dosya | Süre | Durum |
|------|-------|------|-------|
| **Phase 1** | ~~Project Setup~~ | ~~30 min~~ | ✅ Tamamlandı |
| **Phase 2** | `TASK-02-database-migration.md` | 1 saat | 🔜 Sonraki |
| **Phase 3** | `TASK-03-orm-models.md` | 1.5 saat | ⏳ Bekliyor |
| **Phase 4** | `TASK-04-pydantic-schemas.md` | 1 saat | ⏳ Bekliyor |
| **Phase 5** | `TASK-05-business-services.md` | 2 saat | ⏳ Bekliyor |
| **Phase 6** | `TASK-06-api-routers.md` | 2 saat | ⏳ Bekliyor |
| **Phase 7** | `TASK-07-authentication.md` | 1 saat | ⏳ Bekliyor |
| **Phase 8** | `TASK-08-testing.md` | 1.5 saat | ⏳ Bekliyor |

**Toplam Süre:** ~8 saat (MVP'ye kadar)

---

## 🎯 Her Task'ı Nasıl Kullanmalı?

### Claude Code'a Verirken:

1. **Bir task dosyasını aç** (örn: `TASK-02-database-migration.md`)
2. **Tüm içeriği kopyala**
3. **Claude Code'a yapıştır** ve şunu ekle:
   ```
   Yukarıdaki task'ı tam olarak uygula. Tüm dosyaları oluştur ve
   başarı kriterlerini kontrol et.
   ```

### Task Tamamlandığında:

1. ✅ README.md'deki durumu güncelle (⏳ → ✅)
2. ✅ Başarı kriterlerini kontrol et
3. ✅ Bir sonraki task'a geç

---

## 📚 Ön Okuma (Önemli!)

Her task'a başlamadan önce bu dökümanları oku:

1. **BACKEND_PROJECT_SPECIFICATION.md** - Tam API spesifikasyonu
2. **DATABASE_VISUAL_SCHEMA.md** - Database şeması ve ilişkiler
3. **CLAUDE.md** - Kod standartları ve kısıtlamalar
4. **BACKEND_ARCHITECTURE_ANALYSIS.md** - Mimari kararlar

---

## ⚠️ Önemli Kurallar

1. **Async/Await Zorunlu**: Tüm I/O işlemleri async olmalı
2. **Type Hints Zorunlu**: Her fonksiyon type hint içermeli
3. **Service Layer Pattern**: Router → Service → Model → Database
4. **Pydantic Schemas**: ORM modellerini direkt döndürme
5. **FastAPI Dependency Injection**: `Depends()` kullan

---

## 🚀 Hızlı Başlangıç

```bash
# Backend projesine git
cd /Users/ali/Documents/Projects/canvas-app-backend

# Virtual environment aktive et
source venv/bin/activate

# İlk task'ı aç
cat tasks/TASK-02-database-migration.md

# Claude Code'a yapıştır ve başla!
```

---

**Son Güncelleme:** 2026-01-18
**Toplam Task:** 8 (7 kaldı)
**Hedef:** Production-ready backend API
