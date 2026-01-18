# Database Tables Documentation

Bu klasör, veritabanındaki her tablonun detaylı dokümantasyonunu içerir.

---

## 📋 Tablo Listesi

| # | Tablo | Açıklama | Tip |
|---|-------|----------|-----|
| 01 | [users](01-users/) | Kullanıcı kimlik doğrulama ve profiller | Core System |
| 02 | [token_blacklist](02-token-blacklist/) | JWT token revocation | Security |
| 03 | [fields](03-fields/) | Field tanımları (text, number, vb.) | Metadata |
| 04 | [objects](04-objects/) | Object tanımları (Contact, Company, vb.) | Metadata |
| 05 | [object_fields](05-object-fields/) | Object-Field bağlantıları | Mapping |
| 06 | [records](06-records/) | Gerçek veri kayıtları (JSONB) | Data |
| 07 | [relationships](07-relationships/) | Object-Object ilişkileri | Metadata |
| 08 | [relationship_records](08-relationship-records/) | Record-Record bağlantıları | Mapping |
| 09 | [applications](09-applications/) | Uygulama tanımları (CRM, ITSM) | System |
| 10 | [alembic_version](10-alembic-version/) | Migration version tracking | System |

---

## 🗂️ Dokümantasyon Yapısı

Her tablo klasöründe şu dosyalar bulunur:

### README.md
- Genel bakış
- Tablo özellikleri
- Kolon detayları
- İlişkiler
- Index'ler
- Örnek kullanımlar
- Örnek sorgular
- Best practices

---

## 🔗 Tablo İlişkileri Özeti

### Core Tables (Metadata)

```
users
  └─► fields (created_by)
  └─► objects (created_by)

fields ◄─┐
         ├─► object_fields ◄─┐
objects ◄─┘                  │
                             │
                         defines
                             │
                        ┌────▼────┐
                        │ records │
                        └────┬────┘
                             │
relationships ──► relationship_records ◄─┘
```

### Key Relationships

1. **objects ←→ fields** (N:N via object_fields)
   - Object'ler hangi field'ları kullanır

2. **objects → records** (1:N)
   - Object tanımı → Gerçek veri kayıtları

3. **objects ←→ objects** (N:N via relationships)
   - Object'ler arasında ilişkiler

4. **records ←→ records** (N:N via relationship_records)
   - Kayıtlar arasında bağlantılar

---

## 📊 Tablo Tipleri

### 1. Core System Tables
- **users**: Kimlik doğrulama
- **token_blacklist**: Token yönetimi
- **alembic_version**: Migration tracking

### 2. Metadata Tables
- **fields**: Field tanımları
- **objects**: Object tanımları
- **relationships**: İlişki tanımları

### 3. Mapping Tables
- **object_fields**: Object-Field bağlantıları
- **relationship_records**: Record-Record bağlantıları

### 4. Data Tables
- **records**: Gerçek veri (JSONB storage)

### 5. Application Tables
- **applications**: Uygulama yapılandırmaları

---

## 🎯 En Sık Kullanılan Tablolar

### 1. records (Yüksek Hacim)
- En çok veri içerir
- JSONB hybrid model
- Performans critical
- Partitioning önerilir

### 2. object_fields (Sık Güncellenen)
- Object-field bağlantıları
- Display order yönetimi
- Required/visible flags

### 3. relationship_records (İlişki Verileri)
- Record bağlantıları
- İlişki metadata'sı
- Çift yönlü sorgular

---

## 🔍 Hızlı Referans

### ID Formatları

| Tablo | Prefix | Örnek |
|-------|--------|-------|
| users | (UUID) | 550e8400-e29b-41d4-a716-446655440000 |
| fields | fld_ | fld_a1b2c3d4 |
| objects | obj_ | obj_e5f6g7h8 |
| object_fields | ofd_ | ofd_i9j0k1l2 |
| records | rec_ | rec_m3n4o5p6 |
| relationships | rel_ | rel_q7r8s9t0 |
| relationship_records | rrec_ | rrec_u1v2w3x4 |
| applications | app_ | app_y5z6a7b8 |

### CASCADE Davranışları

| Parent | Child | Action |
|--------|-------|--------|
| objects → object_fields | CASCADE | ✅ |
| fields → object_fields | RESTRICT | ⚠️ |
| objects → records | CASCADE | ✅ |
| relationships → relationship_records | CASCADE | ✅ |
| records → relationship_records | CASCADE | ✅ |

---

## 📈 Performans İpuçları

### 1. Her Zaman object_id ile Filtrele (records)
```sql
WHERE object_id = 'obj_contact'  -- Index kullanır
```

### 2. primary_value Kullan (text search)
```sql
WHERE primary_value ILIKE '%search%'  -- 7x daha hızlı
```

### 3. created_at Index'i Kullan
```sql
ORDER BY created_at DESC  -- Index kullanır
```

### 4. JSONB GIN Index (sık sorgulanan path'ler)
```sql
CREATE INDEX idx_email ON records USING GIN ((data->'fld_email'));
```

---

## 🔐 Güvenlik Notları

1. **Password Hashing**: bcrypt (cost: 12)
2. **JWT Token**: 1 saat geçerlilik
3. **Tenant Isolation**: Row-level (tenant_id)
4. **Soft Delete**: is_active bayrakları kullan
5. **Created/Updated By**: Audit trail için

---

## 📚 Ek Dokümantasyon

- [Database Schema Overview](../DATABASE_SCHEMA.md)
- [Entity Relationship Diagram](../DATABASE_ER_DIAGRAM.md)
- [Table Examples](../TABLE_EXAMPLES.md)
- [API Documentation](../../api/)

---

**Last Updated:** 2026-01-18
**Database:** PostgreSQL 16 (Supabase Local)
**Status:** ✅ All tables documented
