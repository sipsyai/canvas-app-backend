# 📋 Canvas App Backend - Task List

Bu klasör, backend'i production-ready hale getirmek için yapılması gereken tüm taskları içerir.

---

## 📂 Klasör Yapısı

```
tasks/
├── priority-1-critical/      # 🔴 KRİTİK - 1-2 gün içinde yapılmalı
│   ├── 01-field-model-schema-update.md
│   ├── 02-object-model-schema-update.md
│   ├── 03-plural-label-rename.md
│   ├── 04-datetime-utc-migration.md
│   └── 05-test-coverage-expansion.md
│
├── priority-2-important/     # 🟡 ÖNEMLİ - 2-3 gün içinde yapılmalı
│   ├── 05-system-fields-seed-data.md
│   ├── 06-user-object-implementation.md
│   └── 07-rls-policies-verification.md
│
├── priority-3-improvements/  # 🟢 İYİLEŞTİRME - 1-2 hafta içinde yapılabilir
│   ├── 08-openapi-docs-enhancement.md
│   ├── 09-error-handling-standardization.md
│   └── 10-logging-implementation.md
│
└── README.md                 # Bu dosya
```

---

## 🚀 Hızlı Başlangıç

### Claude ile Çalışma

Her task dosyası başında `🤖 CLAUDE PROMPT` bloğu var. Dosyayı Claude'a vererek direkt çalıştırabilirsiniz:

```bash
# Örnek 1: Task dosyasını Claude'a göster
cat tasks/priority-1-critical/01-field-model-schema-update.md

# Örnek 2: Claude'a prompt ver
# Bu dosyadaki "🤖 CLAUDE PROMPT" bloğunu kopyala-yapıştır
```

### Manuel Çalışma

Her task dosyası şunları içerir:
- ✅ **Objective:** Ne yapılacak
- 🎯 **Problem:** Neden gerekli
- 📝 **Implementation Steps:** Adım adım rehber
- ✅ **Acceptance Criteria:** Ne zaman tamamlanmış sayılır
- 🧪 **Testing:** Nasıl test edilir
- 🚨 **Rollback Plan:** Hata durumunda ne yapılır

---

## 📊 Task Summary

### Priority 1: Critical (5 tasks - 2-3 days)

| # | Task | Estimated Time | Status |
|---|------|----------------|--------|
| 01 | Field Model Schema Update | 2-3 hours | ⏳ Pending |
| 02 | Object Model Schema Update | 1-2 hours | ⏳ Pending |
| 03 | Plural Label Rename | 30 min | ⏳ Pending |
| 04 | Datetime UTC Migration | 1 hour | ⏳ Pending |
| 05 | Test Coverage Expansion | 3-4 hours | ⏳ Pending |

**Total:** ~8-10 hours (1-2 days)

---

### Priority 2: Important (3 tasks - 2-3 days)

| # | Task | Estimated Time | Status |
|---|------|----------------|--------|
| 06 | System Fields Seed Data | 1 hour | ⏳ Pending |
| 07 | User Object Implementation | 2-3 hours | ⏳ Pending |
| 08 | RLS Policies Verification | 1-2 hours | ⏳ Pending |

**Total:** ~5-6 hours (1 day)

---

### Priority 3: Improvements (3 tasks - 1-2 days)

| # | Task | Estimated Time | Status |
|---|------|----------------|--------|
| 09 | OpenAPI Docs Enhancement | 1-2 hours | ⏳ Pending |
| 10 | Error Handling Standardization | 2-3 hours | ⏳ Pending |
| 11 | Logging Implementation | 1-2 hours | ⏳ Pending |

**Total:** ~5-7 hours (1 day)

---

## 🎯 Önerilen Çalışma Sırası

### Hızlı Fix Yöntemi (2 gün - %90 Ready)

Sadece **Priority 1** task'ları yapın:

```
Day 1:
  ✅ Task 01: Field Model Schema Update (2-3h)
  ✅ Task 02: Object Model Schema Update (1-2h)
  ✅ Task 03: Plural Label Rename (30min)
  ✅ Task 04: Datetime UTC Migration (1h)

Day 2:
  ✅ Task 05: Test Coverage Expansion (3-4h)
```

**Sonuç:** Backend %90 production-ready ✅

---

### Tam Tamamlama Yöntemi (5-7 gün - %100 Ready)

Tüm priority'leri sırayla yapın:

```
Day 1-2: Priority 1 (Critical)
Day 3: Priority 2 (Important)
Day 4-5: Priority 3 (Improvements)
Day 6-7: Final testing + deployment preparation
```

**Sonuç:** Backend %100 production-ready ✅

---

## 🔥 Kritik Noktalar

### 1. Task Dependency (Bağımlılıklar)

Bazı task'lar diğerlerine bağlı:

```
Task 01 (Field Schema)
  └──> Task 06 (System Fields) - Requires is_system_field column
  └──> Task 02 (Object Schema) - Related changes

Task 02 (Object Schema)
  └──> Task 07 (User Object) - Uses views JSONB

Task 06 (System Fields)
  └──> Task 07 (User Object) - System fields reference User
```

**Öneri:** Task numaralarına göre sırayla yapın.

---

### 2. Migration Sırası

**ÖNEMLİ:** Migration'lar sırayla çalıştırılmalı:

```bash
# 1. Field schema update
alembic upgrade head

# 2. Object schema update
alembic upgrade head

# 3. System fields seed data
alembic upgrade head

# 4. User object
alembic upgrade head
```

**Her migration'dan sonra:**
```bash
# Verify migration
psql $DATABASE_URL -c "\d fields"
psql $DATABASE_URL -c "\d objects"

# Run tests
pytest tests/
```

---

### 3. Rollback Hazırlığı

Her task için rollback planı var:

```bash
# Eğer bir şeyler ters giderse:
alembic downgrade -1

# Migration history'yi kontrol et:
alembic history

# Belirli bir versiyona geri dön:
alembic downgrade <revision_id>
```

---

## 📈 Progress Tracking

### Nasıl İlerler Kaydedilir?

Her task dosyasının sonunda **Acceptance Criteria** checklist'i var:

```markdown
## ✅ Acceptance Criteria

- [ ] Column exists in database
- [ ] Migration runs successfully
- [ ] Tests pass
- [ ] API endpoint works
```

Checklist'i güncelleyin:

```markdown
- [x] Column exists in database  ✅ DONE
- [x] Migration runs successfully  ✅ DONE
- [ ] Tests pass  ⏳ IN PROGRESS
- [ ] API endpoint works
```

---

## 🧪 Testing Strategy

Her task için test şablonları var:

### Unit Test
```python
# tests/test_services/test_field_service.py
async def test_field_category_filter(db_session, user_id):
    # Test implementation
    pass
```

### API Test
```bash
# Manual cURL test
curl -X GET "http://localhost:8000/api/fields?category=System" \
  -H "Authorization: Bearer $TOKEN"
```

### Integration Test
```python
# tests/test_integration.py
async def test_end_to_end_flow():
    # Create field → Create object → Add field to object → Create record
    pass
```

---

## 🔒 Güvenlik Kontrolleri

Her task'ta dikkat edilmesi gerekenler:

- ✅ **SQL Injection:** Parametrized queries kullanıldı mı?
- ✅ **Auth Bypass:** RLS policies çalışıyor mu?
- ✅ **Data Leak:** created_by kontrolü var mı?
- ✅ **JSONB Injection:** Input validation yapıldı mı?

---

## 📞 Yardım & Destek

### Task İle İlgili Sorun Durumunda

1. **Task dosyasını tekrar oku** - Detaylı adımlar var
2. **Acceptance Criteria'yı kontrol et** - Ne eksik?
3. **Rollback yap** - Temiz baştan başla
4. **Claude'a sor** - Task dosyasını Claude'a göster

### Migration Hatası Durumunda

```bash
# 1. Migration history'yi kontrol et
alembic history

# 2. Mevcut versiyonu gör
alembic current

# 3. Downgrade yap
alembic downgrade -1

# 4. Database'i kontrol et
psql $DATABASE_URL -c "\d+ fields"
```

---

## 🎉 Tamamlanma Kriterleri

Backend hazır sayılır eğer:

### Minimum (Quick Fix)
- ✅ Priority 1 tasks tamamlandı (%90 ready)
- ✅ Tüm migration'lar çalıştı
- ✅ Test coverage %70+
- ✅ API endpoints çalışıyor

### Full (Complete)
- ✅ Tüm priority'ler tamamlandı (%100 ready)
- ✅ Test coverage %90+
- ✅ OpenAPI docs güncel
- ✅ Logging eklenmiş
- ✅ Error handling standardize

---

## 📚 İlgili Dokümanlar

- `/BACKEND_ARCHITECTURE_ANALYSIS.md` - Mimari kararlar
- `/DATABASE_VISUAL_SCHEMA.md` - Database şeması
- `/BACKEND_PROJECT_SPECIFICATION.md` - API spesifikasyonu
- `/CLAUDE.md` - Claude Code geliştirme kuralları

---

**Son Güncelleme:** 2026-01-18
**Toplam Süre:** 5-7 gün (tam tamamlama)
**Hızlı Süre:** 2 gün (kritik task'lar)

**Her task için Claude prompt hazır! Sadece dosyayı aç ve başla! 🚀**
