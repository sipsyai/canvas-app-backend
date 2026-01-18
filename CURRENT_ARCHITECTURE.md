# Mevcut Supabase Mimarisi - Durum Raporu

**Tarih:** 2026-01-18
**Durum:** ✅ **LOCAL SUPABASE ÇALIŞIYOR**

---

## ✅ MEVCUDİYET ANALİZİ

### 1. Local Supabase Status

**Docker Containers (12/12 Running - 19 saat uptime):**
```
✅ supabase_db_canvas-app          - PostgreSQL (port 54322)
✅ supabase_kong_canvas-app        - API Gateway (port 54321)
✅ supabase_studio_canvas-app      - Dashboard (port 54323)
✅ supabase_auth_canvas-app        - Authentication
✅ supabase_realtime_canvas-app    - Realtime subscriptions
✅ supabase_rest_canvas-app        - PostgREST API
✅ supabase_storage_canvas-app     - File storage
✅ supabase_edge_runtime_canvas-app - Edge functions
✅ supabase_pg_meta_canvas-app     - Metadata API
✅ supabase_vector_canvas-app      - Vector/embeddings
✅ supabase_analytics_canvas-app   - Analytics (port 54327)
✅ supabase_inbucket_canvas-app    - Email testing (port 54324)
```

**Access Points:**
- **API:** http://127.0.0.1:54321
- **Dashboard:** http://127.0.0.1:54323
- **PostgreSQL:** localhost:54322

**Environment Variables (.env):**
```bash
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
VITE_ENABLE_SUPABASE=false  # ⚠️ Şu anda kapalı!
```

---

## 🗄️ DATABASE SCHEMA (Mevcut)

### Applied Migrations (3)

**1. Initial Schema (20260117000000)**
- Temel tablolar

**2. Record Template Architecture (20260117140000)**
- Template-based yaklaşım

**3. Object Model Architecture (20260117210000)** ⭐ **AKTIF**
- Object-centric architecture
- Salesforce/Airtable-style

### Current Tables (5)

#### **1. `objects`** - Core object definitions
```sql
CREATE TABLE objects (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  plural_name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  is_custom BOOLEAN DEFAULT true,

  -- JSONB columns for flexibility
  fields JSONB NOT NULL DEFAULT '[]',           -- Array of Field objects
  relationships JSONB NOT NULL DEFAULT '[]',     -- Array of Relationship objects
  views JSONB NOT NULL DEFAULT '{}',            -- Forms, Tables, Kanbans, Calendars
  permissions JSONB NOT NULL DEFAULT '{}',       -- Access control

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id)
);
```

**Özellikler:**
- JSONB-based schema (çok esnek)
- Field definitions JSONB array olarak
- Views tüm tipleri içinde barındırıyor
- GIN indexes (fast JSONB queries)

---

#### **2. `applications`** - Application containers
```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,

  objects JSONB NOT NULL DEFAULT '[]',         -- Object IDs array
  navigation JSONB NOT NULL DEFAULT '[]',      -- Menu structure
  permissions JSONB NOT NULL DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),
  published_at TIMESTAMPTZ
);
```

**Kullanım:**
- CRM, ITSM gibi uygulamalar
- Multiple objects'i grupla
- Navigation menüsü tanımla

---

#### **3. `records`** - Universal data storage
```sql
CREATE TABLE records (
  id UUID PRIMARY KEY,
  object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

  -- Dynamic JSONB data
  data JSONB NOT NULL DEFAULT '{}',  -- { "field_id_1": "value1", ... }

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),
  updated_by UUID REFERENCES auth.users(id)
);
```

**Özellikler:**
- Tüm object'lerin data'sı burada
- JSONB format: `{ "fld_001": "Ali Yılmaz", "fld_002": "ali@example.com" }`
- GIN index for fast queries
- Her object için ayrı tablo YOK (unified storage)

---

#### **4. `relationship_records`** - N:N junction table
```sql
CREATE TABLE relationship_records (
  id UUID PRIMARY KEY,
  relationship_id TEXT NOT NULL,
  from_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
  to_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Kullanım:**
- Many-to-many relationships
- Örn: Contact ↔ Opportunity
- Metadata: role, start_date, etc.

---

#### **5. `field_templates`** - Reusable field configs
```sql
CREATE TABLE field_templates (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  field_config JSONB NOT NULL,  -- Full Field object
  category TEXT,
  usage_count INTEGER DEFAULT 0,
  is_global BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id)
);
```

**Kullanım:**
- Field library (Email, Phone, etc.)
- Reusable across objects
- Global templates (tüm kullanıcılar için)

---

## 🔐 ROW LEVEL SECURITY (RLS)

**Tüm tablolarda aktif:**
- ✅ Users can only see/edit their own objects
- ✅ Users can only see/edit records from their objects
- ✅ Cascade permissions (records inherit from objects)
- ✅ Global field templates accessible to all

**Policies:**
```sql
-- Objects: User isolation
objects_select_policy: created_by = auth.uid() OR is_custom = false
objects_insert_policy: created_by = auth.uid()
objects_update_policy: created_by = auth.uid()
objects_delete_policy: created_by = auth.uid()

-- Records: Cascade from objects
records_select_policy: EXISTS (SELECT 1 FROM objects WHERE created_by = auth.uid())
records_insert_policy: created_by = auth.uid() AND object owner check
records_update_policy: object owner check
records_delete_policy: object owner check
```

---

## 🛠️ HELPER FUNCTIONS (PostgreSQL)

### 1. `get_object_records()`
```sql
-- Get all records for an object (with pagination)
SELECT * FROM get_object_records(
  p_object_id := 'obj_123',
  p_limit := 100,
  p_offset := 0
);
```

### 2. `get_related_records()`
```sql
-- Get related records via relationship
SELECT * FROM get_related_records(
  p_record_id := 'rec_456',
  p_relationship_id := 'rel_001',
  p_direction := 'from'  -- or 'to'
);
```

### 3. `search_records()`
```sql
-- Search by field value
SELECT * FROM search_records(
  p_object_id := 'obj_123',
  p_field_id := 'fld_name',
  p_search_term := 'Ali'
);
```

---

## 📦 FRONTEND STATE MANAGEMENT

### Zustand Stores (Mevcut)

**1. `src/stores/objectStore.ts`** ✅ MEVCUT
- Object definitions management
- Field CRUD operations
- Relationship management
- View generation
- **localStorage-based** (henüz Supabase'e bağlı değil)

**2. `src/stores/objectRecordStore.ts`** ✅ MEVCUT
- Record data management
- CRUD operations
- Search & filtering
- **localStorage-based** (henüz Supabase'e bağlı değil)

**3. `src/stores/authStore.ts`** ✅ MEVCUT
- User authentication state
- Login/logout
- **Supabase Auth entegrasyonu VAR**

**4. `src/stores/workspaceStore.ts`** ✅ MEVCUT
- Workspace settings
- System fields config

---

## 🔌 SUPABASE CLIENT

**File:** `src/lib/supabase.ts`
```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient<Database>(supabaseUrl, supabaseAnonKey)
  : null;

export const isSupabaseEnabled = (): boolean => {
  return (
    import.meta.env.VITE_ENABLE_SUPABASE === 'true' &&
    supabase !== null
  );
};
```

**Durum:**
- ✅ Client configured
- ✅ Type-safe (Database types)
- ⚠️ **ENABLE FLAG = false** (kullanılmıyor)

---

## 🔄 İKİ MİMARİ KARŞILAŞTIRMASI

### A) Mevcut Sistem (Object-Centric - JSONB)

**Avantajlar:**
- ✅ Çok esnek (schema değişiklikleri kolay)
- ✅ Daha az tablo (5 vs 8)
- ✅ Tek query ile tüm field'lar
- ✅ Migration kolay
- ✅ ZATEN KURULU VE ÇALIŞIYOR

**Dezavantajlar:**
- ❌ JSONB queries biraz yavaş (büyük data'da)
- ❌ Field-level indexing zor
- ❌ Type safety JSONB içinde yok

**Tablo yapısı:**
```
objects (schema definition)
  ↓
records (JSONB data: {field_id: value})
  ↓
relationship_records (N:N links)
```

---

### B) database-schema-v2.sql (EAV Pattern - Normalized)

**Avantajlar:**
- ✅ Normalize edilmiş (proper relational)
- ✅ Field-level indexes (fast queries)
- ✅ Type-safe columns (value_text, value_number, etc.)
- ✅ Better for complex queries

**Dezavantajlar:**
- ❌ Daha çok tablo (8 tablo)
- ❌ Multiple JOINs gerekli (performance hit)
- ❌ Schema değişiklikleri zor
- ❌ HENüZ KURULU DEĞİL

**Tablo yapısı:**
```
record_templates (schema definition)
  ↓
template_fields (field definitions)
  ↓
records (record metadata)
  ↓
record_values (EAV: one row per field per record)
  ↓
record_relationships + record_links
```

---

## 🎯 ŞİMDİ NE YAPMAMIZ GEREK?

### Seçenek 1: Mevcut Sistemi Kullan (ÖNERİLEN ✅)

**Durum:**
- ✅ Supabase çalışıyor
- ✅ Schema kurulu
- ✅ RLS configured
- ✅ Helper functions ready
- ⚠️ Frontend HENÜZ Supabase'e bağlı değil (localStorage kullanıyor)

**Yapılacaklar (2-3 gün):**

1. **Enable Supabase** (30 dakika)
   ```bash
   # .env
   VITE_ENABLE_SUPABASE=true  # false → true
   ```

2. **Connect objectStore to Supabase** (4 saat)
   - `createObject()` → `supabase.from('objects').insert()`
   - `updateObject()` → `supabase.from('objects').update()`
   - `deleteObject()` → `supabase.from('objects').delete()`
   - `getObject()` → `supabase.from('objects').select()`

3. **Connect objectRecordStore to Supabase** (6 saat)
   - `createRecord()` → `supabase.from('records').insert()`
   - `updateRecord()` → Transform data to JSONB format
   - `getRecords()` → Flatten JSONB back to object
   - `searchRecords()` → Use `search_records()` function

4. **Test & Verify** (2 saat)
   - Create object
   - Add fields
   - Create records
   - Query/filter
   - Relationships

**Timeline:** 2-3 gün MAX

---

### Seçenek 2: Migrate to EAV (database-schema-v2.sql)

**Durum:**
- ❌ Yeni migration gerekli
- ❌ Mevcut data migrate edilmeli
- ❌ Frontend store'ları yeniden yazılmalı
- ❌ Daha karmaşık queries

**Yapılacaklar (1-2 hafta):**
1. Apply database-schema-v2.sql
2. Migrate JSONB data to EAV
3. Rewrite objectStore → recordTemplateStore
4. Rewrite objectRecordStore → recordService (EAV)
5. Update all components
6. Test everything

**Timeline:** 1-2 HAFTA

---

## 💡 TAVSİYE

**SEÇENEK 1'İ KULLAN!** İşte nedenler:

1. ✅ **Zaten çalışıyor** - Neden tekrar başlayalım?
2. ✅ **2-3 gün vs 1-2 hafta** - Net kazanç
3. ✅ **Daha basit** - JSONB = esnek ve hızlı development
4. ✅ **RLS hazır** - Auth sistem kurulu
5. ✅ **Helper functions** - PostgreSQL functions ready
6. ✅ **Frontend %80 hazır** - Sadece Supabase connection ekle

**EAV'ye ihtiyacımız ne zaman olur?**
- 100,000+ records (performance critical)
- Çok complex filtering
- Field-level indexing şart

Şu an için JSONB-based sistem **MÜKEMMEL**! 🎯

---

## 🚀 NEXT STEPS (Hemen Başlayabiliriz)

### Adım 1: Supabase Enable (5 dakika)
```bash
# .env dosyasında
VITE_ENABLE_SUPABASE=true
```

### Adım 2: objectStore'u Supabase'e Bağla (4 saat)

**File:** `src/stores/objectStore.ts`

Şu anki kod:
```typescript
createObject: (objectData) => {
  // localStorage'a kaydet
  set((state) => ({ objects: [...state.objects, newObject] }));
}
```

Yeni kod:
```typescript
createObject: async (objectData) => {
  // 1. Supabase'e kaydet
  const { data, error } = await supabase
    .from('objects')
    .insert({
      name: objectData.name,
      plural_name: objectData.pluralName,
      icon: objectData.icon,
      fields: objectData.fields,
      relationships: objectData.relationships,
      views: objectData.views,
    })
    .select()
    .single();

  if (error) throw error;

  // 2. State'i güncelle
  set((state) => ({ objects: [...state.objects, mapDatabaseToObject(data)] }));

  return data.id;
}
```

### Adım 3: Test (1 saat)
```typescript
// Test: Create object
const objectId = await objectStore.createObject({
  name: 'contacts',
  pluralName: 'Contacts',
  fields: [
    { name: 'full_name', type: 'text', label: 'Full Name' },
    { name: 'email', type: 'email', label: 'Email' }
  ]
});

// Verify in Supabase Dashboard
// http://127.0.0.1:54323/project/default/editor
```

---

## ❓ SORULAR

1. **Mevcut object-centric mimari ile devam edelim mi?** ✅ ÖNERİLİR
2. **database-schema-v2.sql (EAV) gerekli mi?** ❌ Şimdilik gerek yok
3. **Ne zaman başlıyoruz?** 🚀 Hemen!

---

**Status:** ✅ Ready to Connect Frontend to Supabase
**Next Action:** Enable Supabase flag and update objectStore
**Estimated Time:** 2-3 days
