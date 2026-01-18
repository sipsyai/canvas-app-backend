# Frontend Developer Guide - Canvas App Backend API

**Frontend geliştiriciler için kapsamlı API kullanım rehberi**

> Bu dokümanda tüm backend API'lerini, nasıl kullanacağınızı, TypeScript tiplerini, best practice'leri ve yaygın hataları bulacaksınız.

## 📚 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Authentication (Kimlik Doğrulama)](#authentication)
3. [API Kategorileri](#api-kategorileri)
   - [Fields API](#fields-api)
   - [Objects API](#objects-api)
   - [Object-Fields API](#object-fields-api)
   - [Records API](#records-api)
   - [Relationships API](#relationships-api)
   - [Relationship-Records API](#relationship-records-api)
   - [Applications API](#applications-api)
4. [Workflow Örnekleri](#workflow-örnekleri)
5. [TypeScript Tipleri](#typescript-tipleri)
6. [Best Practices](#best-practices)
7. [Error Handling](#error-handling)
8. [Common Pitfalls](#common-pitfalls)

---

## Genel Bakış

### Backend URL

```typescript
const API_BASE_URL = "http://localhost:8000"; // Development
// Production: "https://your-domain.com"
```

### API Versiyonu

**Versiyon:** v1.0.0
**Tarih:** 2026-01-18
**Toplam Endpoint:** 34

### Authentication Model

- **Tür:** JWT (JSON Web Token)
- **Algoritma:** HS256
- **Geçerlilik Süresi:** 1 saat
- **Header Format:** `Authorization: Bearer YOUR_JWT_TOKEN`

### Genel Endpoint Yapısı

```
/api/{category}/{endpoint}

Örnekler:
/api/auth/login
/api/fields/{field_id}
/api/records?object_id=obj_contact
```

---

## Authentication

### 1. Register (Yeni Kullanıcı Kaydı)

**Endpoint:** `POST /api/auth/register`
**Public:** Evet (token gerekmez)

#### Request

```typescript
interface RegisterRequest {
  email: string;        // Email formatında
  password: string;     // Min 8 karakter
  full_name: string;    // Tam ad
}
```

#### Fetch Example

```javascript
const register = async (email, password, fullName) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Kullanım
try {
  const user = await register("ali@example.com", "SecurePass123", "Ali Veli");
  console.log("Kayıt başarılı:", user);
} catch (error) {
  console.error("Kayıt hatası:", error.message);
}
```

#### Axios Example

```javascript
import axios from "axios";

const register = async (email, password, fullName) => {
  try {
    const { data } = await axios.post(`${API_BASE_URL}/api/auth/register`, {
      email,
      password,
      full_name: fullName,
    });
    return data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || "Kayıt başarısız");
  }
};
```

#### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "ali@example.com",
  "full_name": "Ali Veli",
  "created_at": "2026-01-18T10:00:00Z"
}
```

---

### 2. Login (Giriş Yap)

**Endpoint:** `POST /api/auth/login`
**Public:** Evet (token gerekmez)

#### Request

```typescript
interface LoginRequest {
  username: string;  // Email (form-data olarak!)
  password: string;  // Password
}
```

**IMPORTANT:** Login endpoint `application/x-www-form-urlencoded` bekler, JSON değil!

#### Fetch Example

```javascript
const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append("username", email);  // NOT email, use "username"!
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Giriş başarısız");
  }

  const data = await response.json();

  // Token'ı localStorage'a kaydet
  localStorage.setItem("access_token", data.access_token);

  return data;
};
```

#### Axios Example

```javascript
import axios from "axios";

const login = async (email, password) => {
  try {
    const { data } = await axios.post(
      `${API_BASE_URL}/api/auth/login`,
      new URLSearchParams({
        username: email,
        password: password,
      }),
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    // Token'ı localStorage'a kaydet
    localStorage.setItem("access_token", data.access_token);

    return data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || "Giriş başarısız");
  }
};
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. Get Current User (Mevcut Kullanıcı)

**Endpoint:** `GET /api/auth/me`
**Protected:** Evet (JWT gerekli)

#### Fetch Example

```javascript
const getCurrentUser = async () => {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Kullanıcı bilgisi alınamadı");
  }

  return await response.json();
};
```

#### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "ali@example.com",
  "full_name": "Ali Veli",
  "created_at": "2026-01-18T10:00:00Z"
}
```

---

### Authentication Helper

Tüm protected endpoint'ler için yardımcı fonksiyon:

```javascript
// utils/api.js
export const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("Token bulunamadı. Lütfen giriş yapın.");
  }
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

// Kullanım
const fields = await fetch(`${API_BASE_URL}/api/fields`, {
  headers: getAuthHeaders(),
});
```

---

## API Kategorileri

## Fields API

Field'lar form alanlarını temsil eder (email, phone, text, number vb.).

### 1. Create Field

**Endpoint:** `POST /api/fields`
**Protected:** Evet

#### Request

```typescript
interface FieldCreateRequest {
  name: string;              // Unique identifier (e.g., "email")
  label: string;             // Display name (e.g., "Email Address")
  type: string;              // Field type: "text", "email", "phone", "number", "date", "textarea", "select", "checkbox"
  category?: string;         // Kategori (e.g., "Contact Info")
  description?: string;      // Açıklama
  is_system_field?: boolean; // Sistem field'ı mı? (default: false)
  config?: {                 // Field konfigürasyonu
    placeholder?: string;
    min?: number;
    max?: number;
    options?: string[];      // Select için seçenekler
    validation?: object;
  };
}
```

#### Example

```javascript
const createField = async (fieldData) => {
  const response = await fetch(`${API_BASE_URL}/api/fields`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(fieldData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Kullanım
const emailField = await createField({
  name: "email",
  label: "Email Address",
  type: "email",
  category: "Contact Info",
  config: {
    placeholder: "example@email.com",
  },
});

console.log(emailField.id); // "fld_abc12345"
```

#### Response

```json
{
  "id": "fld_abc12345",
  "name": "email",
  "label": "Email Address",
  "type": "email",
  "category": "Contact Info",
  "description": null,
  "is_system_field": false,
  "config": {
    "placeholder": "example@email.com"
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": null
}
```

---

### 2. List Fields

**Endpoint:** `GET /api/fields`
**Protected:** Evet

#### Query Parameters

```typescript
interface FieldListParams {
  category?: string;         // Kategoriye göre filtrele
  is_system?: boolean;       // Sistem field'larını filtrele
  page?: number;             // Sayfa numarası (default: 1)
  page_size?: number;        // Sayfa boyutu (default: 50, max: 100)
}
```

#### Example

```javascript
const listFields = async (filters = {}) => {
  const params = new URLSearchParams();

  if (filters.category) params.append("category", filters.category);
  if (filters.is_system !== undefined) params.append("is_system", filters.is_system);
  if (filters.page) params.append("page", filters.page);
  if (filters.page_size) params.append("page_size", filters.page_size);

  const response = await fetch(
    `${API_BASE_URL}/api/fields?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Field'lar alınamadı");
  return await response.json();
};

// Kullanım
const contactFields = await listFields({ category: "Contact Info" });
const allFields = await listFields();
const systemFields = await listFields({ is_system: true });
```

#### Response

```json
[
  {
    "id": "fld_abc12345",
    "name": "email",
    "label": "Email Address",
    "type": "email",
    "category": "Contact Info",
    "config": {},
    "created_at": "2026-01-18T10:00:00Z"
  },
  {
    "id": "fld_xyz67890",
    "name": "phone",
    "label": "Phone Number",
    "type": "phone",
    "category": "Contact Info",
    "config": {},
    "created_at": "2026-01-18T10:05:00Z"
  }
]
```

---

### 3. Get Single Field

**Endpoint:** `GET /api/fields/{field_id}`
**Protected:** Evet

#### Example

```javascript
const getField = async (fieldId) => {
  const response = await fetch(`${API_BASE_URL}/api/fields/${fieldId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) throw new Error("Field bulunamadı");
    throw new Error("Field alınamadı");
  }

  return await response.json();
};

// Kullanım
const field = await getField("fld_abc12345");
```

---

### 4. Update Field

**Endpoint:** `PATCH /api/fields/{field_id}`
**Protected:** Evet

#### Request

```typescript
interface FieldUpdateRequest {
  label?: string;
  category?: string;
  description?: string;
  config?: object;
  // name ve type değiştirilemez!
}
```

#### Example

```javascript
const updateField = async (fieldId, updates) => {
  const response = await fetch(`${API_BASE_URL}/api/fields/${fieldId}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(updates),
  });

  if (!response.ok) throw new Error("Field güncellenemedi");
  return await response.json();
};

// Kullanım
const updatedField = await updateField("fld_abc12345", {
  label: "Primary Email",
  config: {
    placeholder: "your.email@example.com",
    validation: { required: true },
  },
});
```

---

### 5. Delete Field

**Endpoint:** `DELETE /api/fields/{field_id}`
**Protected:** Evet
**Response:** 204 No Content

**WARNING:** Field silindiğinde, ona bağlı tüm object-field ilişkileri de silinir (CASCADE).

#### Example

```javascript
const deleteField = async (fieldId) => {
  const response = await fetch(`${API_BASE_URL}/api/fields/${fieldId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) throw new Error("Field bulunamadı");
    throw new Error("Field silinemedi");
  }

  // 204 No Content - başarılı
  return true;
};

// Kullanım
await deleteField("fld_abc12345");
console.log("Field silindi");
```

---

## Objects API

Object'lar veri tablolarını temsil eder (Contact, Company, Opportunity vb.).

### 1. Create Object

**Endpoint:** `POST /api/objects`
**Protected:** Evet

#### Request

```typescript
interface ObjectCreateRequest {
  name: string;              // Unique identifier (e.g., "contact")
  label: string;             // Singular name (e.g., "Contact")
  plural_name: string;       // Plural name (e.g., "Contacts")
  description?: string;      // Açıklama
  icon?: string;             // Icon name
  color?: string;            // Hex color (e.g., "#3B82F6")
  category?: string;         // Kategori (e.g., "CRM")
  views?: object;            // View konfigürasyonu
  permissions?: object;      // Permission konfigürasyonu
}
```

#### Example

```javascript
const createObject = async (objectData) => {
  const response = await fetch(`${API_BASE_URL}/api/objects`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(objectData),
  });

  if (!response.ok) throw new Error("Object oluşturulamadı");
  return await response.json();
};

// Kullanım
const contactObject = await createObject({
  name: "contact",
  label: "Contact",
  plural_name: "Contacts",
  description: "CRM contacts",
  icon: "user",
  color: "#3B82F6",
  category: "CRM",
});

console.log(contactObject.id); // "obj_abc12345"
```

#### Response

```json
{
  "id": "obj_abc12345",
  "name": "contact",
  "label": "Contact",
  "plural_name": "Contacts",
  "description": "CRM contacts",
  "icon": "user",
  "color": "#3B82F6",
  "category": "CRM",
  "views": null,
  "permissions": null,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": null
}
```

---

### 2. List Objects

**Endpoint:** `GET /api/objects`
**Protected:** Evet

#### Query Parameters

```typescript
interface ObjectListParams {
  category?: string;         // Kategoriye göre filtrele
  page?: number;             // Sayfa numarası
  page_size?: number;        // Sayfa boyutu
}
```

#### Example

```javascript
const listObjects = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.category) params.append("category", filters.category);
  if (filters.page) params.append("page", filters.page);
  if (filters.page_size) params.append("page_size", filters.page_size);

  const response = await fetch(
    `${API_BASE_URL}/api/objects?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Object'ler alınamadı");
  return await response.json();
};

// Kullanım
const crmObjects = await listObjects({ category: "CRM" });
const allObjects = await listObjects();
```

---

### 3. Get Single Object

**Endpoint:** `GET /api/objects/{object_id}`
**Protected:** Evet

#### Example

```javascript
const getObject = async (objectId) => {
  const response = await fetch(`${API_BASE_URL}/api/objects/${objectId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) throw new Error("Object bulunamadı");
    throw new Error("Object alınamadı");
  }

  return await response.json();
};
```

---

### 4. Update Object

**Endpoint:** `PATCH /api/objects/{object_id}`
**Protected:** Evet

#### Request

```typescript
interface ObjectUpdateRequest {
  label?: string;
  plural_name?: string;
  description?: string;
  icon?: string;
  color?: string;
  category?: string;
  views?: object;
  permissions?: object;
  // name değiştirilemez!
}
```

#### Example

```javascript
const updateObject = async (objectId, updates) => {
  const response = await fetch(`${API_BASE_URL}/api/objects/${objectId}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(updates),
  });

  if (!response.ok) throw new Error("Object güncellenemedi");
  return await response.json();
};

// Kullanım
const updated = await updateObject("obj_abc12345", {
  label: "Customer",
  color: "#10B981",
});
```

---

### 5. Delete Object

**Endpoint:** `DELETE /api/objects/{object_id}`
**Protected:** Evet
**Response:** 204 No Content

**WARNING:** Object silindiğinde, ona bağlı tüm record'lar, object-field ilişkileri ve relationship tanımları da silinir (CASCADE).

#### Example

```javascript
const deleteObject = async (objectId) => {
  const response = await fetch(`${API_BASE_URL}/api/objects/${objectId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error("Object silinemedi");
  return true;
};
```

---

## Object-Fields API

Object-Fields, field'ları object'lere bağlar (junction table).

### 1. Add Field to Object

**Endpoint:** `POST /api/object-fields`
**Protected:** Evet

#### Request

```typescript
interface ObjectFieldCreateRequest {
  object_id: string;         // Object ID (obj_xxxxxxxx)
  field_id: string;          // Field ID (fld_xxxxxxxx)
  display_order?: number;    // Sıralama (default: 0)
  is_required?: boolean;     // Zorunlu mu? (default: false)
  is_unique?: boolean;       // Unique mi? (default: false)
  is_primary_field?: boolean;// Primary field mi? (default: false)
  default_value?: any;       // Varsayılan değer
  validation_rules?: object; // Validation kuralları
}
```

#### Example

```javascript
const addFieldToObject = async (objectFieldData) => {
  const response = await fetch(`${API_BASE_URL}/api/object-fields`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(objectFieldData),
  });

  if (!response.ok) throw new Error("Field object'e eklenemedi");
  return await response.json();
};

// Kullanım
const objectField = await addFieldToObject({
  object_id: "obj_contact",
  field_id: "fld_email",
  display_order: 0,
  is_required: true,
  is_unique: true,
  is_primary_field: true,
});

console.log(objectField.id); // "obf_abc12345"
```

#### Response

```json
{
  "id": "obf_abc12345",
  "object_id": "obj_contact",
  "field_id": "fld_email",
  "display_order": 0,
  "is_required": true,
  "is_unique": true,
  "is_primary_field": true,
  "default_value": null,
  "validation_rules": null,
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": null
}
```

---

### 2. List Object Fields

**Endpoint:** `GET /api/object-fields?object_id={object_id}`
**Protected:** Evet

**IMPORTANT:** `object_id` query parameter'ı zorunludur!

#### Example

```javascript
const listObjectFields = async (objectId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/object-fields?object_id=${objectId}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Object field'ları alınamadı");
  return await response.json();
};

// Kullanım
const contactFields = await listObjectFields("obj_contact");

// display_order'a göre sırala
contactFields.sort((a, b) => a.display_order - b.display_order);
```

---

### 3. Get Single Object-Field

**Endpoint:** `GET /api/object-fields/{object_field_id}`
**Protected:** Evet

#### Example

```javascript
const getObjectField = async (objectFieldId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/object-fields/${objectFieldId}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Object-field alınamadı");
  return await response.json();
};
```

---

### 4. Update Object-Field

**Endpoint:** `PATCH /api/object-fields/{object_field_id}`
**Protected:** Evet

#### Request

```typescript
interface ObjectFieldUpdateRequest {
  display_order?: number;
  is_required?: boolean;
  is_unique?: boolean;
  is_primary_field?: boolean;
  default_value?: any;
  validation_rules?: object;
  // object_id ve field_id değiştirilemez!
}
```

#### Example

```javascript
const updateObjectField = async (objectFieldId, updates) => {
  const response = await fetch(
    `${API_BASE_URL}/api/object-fields/${objectFieldId}`,
    {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify(updates),
    }
  );

  if (!response.ok) throw new Error("Object-field güncellenemedi");
  return await response.json();
};

// Kullanım
await updateObjectField("obf_abc12345", {
  display_order: 5,
  is_required: false,
});
```

---

### 5. Remove Field from Object

**Endpoint:** `DELETE /api/object-fields/{object_field_id}`
**Protected:** Evet
**Response:** 204 No Content

#### Example

```javascript
const removeFieldFromObject = async (objectFieldId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/object-fields/${objectFieldId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) throw new Error("Field object'ten kaldırılamadı");
  return true;
};
```

---

## Records API

Record'lar object'lerin veri kayıtlarıdır. JSONB ile dinamik field değerleri saklanır.

### 1. Create Record

**Endpoint:** `POST /api/records`
**Protected:** Evet

#### Request

```typescript
interface RecordCreateRequest {
  object_id: string;         // Object ID (obj_xxxxxxxx)
  data: {                    // JSONB field değerleri
    [fieldId: string]: any;  // fld_email: "ali@example.com"
  };
  primary_value?: string;    // Primary field değeri (auto-set)
}
```

#### Example

```javascript
const createRecord = async (recordData) => {
  const response = await fetch(`${API_BASE_URL}/api/records`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(recordData),
  });

  if (!response.ok) throw new Error("Record oluşturulamadı");
  return await response.json();
};

// Kullanım
const contact = await createRecord({
  object_id: "obj_contact",
  data: {
    fld_email: "ali@example.com",
    fld_phone: "+90 555 1234567",
    fld_company: "Acme Corp",
    fld_title: "CEO",
  },
});

console.log(contact.id); // "rec_abc12345"
console.log(contact.primary_value); // "ali@example.com" (otomatik set edilir)
```

#### Response

```json
{
  "id": "rec_abc12345",
  "object_id": "obj_contact",
  "data": {
    "fld_email": "ali@example.com",
    "fld_phone": "+90 555 1234567",
    "fld_company": "Acme Corp",
    "fld_title": "CEO"
  },
  "primary_value": "ali@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": null,
  "updated_by": null
}
```

---

### 2. List Records

**Endpoint:** `GET /api/records?object_id={object_id}`
**Protected:** Evet

**IMPORTANT:** `object_id` query parameter'ı zorunludur!

#### Query Parameters

```typescript
interface RecordListParams {
  object_id: string;         // REQUIRED - Object ID
  page?: number;             // Sayfa numarası (default: 1)
  page_size?: number;        // Sayfa boyutu (default: 50, max: 100)
}
```

#### Example

```javascript
const listRecords = async (objectId, page = 1, pageSize = 50) => {
  const params = new URLSearchParams({
    object_id: objectId,
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/records?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Record'lar alınamadı");
  return await response.json();
};

// Kullanım
const contacts = await listRecords("obj_contact");
const contactsPage2 = await listRecords("obj_contact", 2, 50);
```

#### Response

```json
[
  {
    "id": "rec_abc12345",
    "object_id": "obj_contact",
    "data": {
      "fld_email": "ali@example.com",
      "fld_phone": "+90 555 1234567"
    },
    "primary_value": "ali@example.com",
    "created_at": "2026-01-18T10:00:00Z"
  },
  {
    "id": "rec_xyz67890",
    "object_id": "obj_contact",
    "data": {
      "fld_email": "ahmet@example.com",
      "fld_phone": "+90 555 9876543"
    },
    "primary_value": "ahmet@example.com",
    "created_at": "2026-01-18T10:05:00Z"
  }
]
```

---

### 3. Get Single Record

**Endpoint:** `GET /api/records/{record_id}`
**Protected:** Evet

#### Example

```javascript
const getRecord = async (recordId) => {
  const response = await fetch(`${API_BASE_URL}/api/records/${recordId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) throw new Error("Record bulunamadı");
    throw new Error("Record alınamadı");
  }

  return await response.json();
};

// Kullanım
const contact = await getRecord("rec_abc12345");
console.log(contact.data.fld_email); // "ali@example.com"
```

---

### 4. Update Record

**Endpoint:** `PATCH /api/records/{record_id}`
**Protected:** Evet

**IMPORTANT:** Update işlemi JSONB field'ları **MERGE** eder (overwrite etmez)!

#### Request

```typescript
interface RecordUpdateRequest {
  data: {                    // Güncellenecek field'lar
    [fieldId: string]: any;
  };
  primary_value?: string;    // Primary field değeri (auto-update)
}
```

#### Example

```javascript
const updateRecord = async (recordId, updates) => {
  const response = await fetch(`${API_BASE_URL}/api/records/${recordId}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(updates),
  });

  if (!response.ok) throw new Error("Record güncellenemedi");
  return await response.json();
};

// Kullanım
// Mevcut data: { fld_email: "ali@example.com", fld_phone: "+90 555 1234567" }
const updated = await updateRecord("rec_abc12345", {
  data: {
    fld_phone: "+90 555 9999999",  // Sadece phone güncellenir
    fld_company: "New Corp",       // Yeni field eklenir
  },
});

// Sonuç data:
// {
//   fld_email: "ali@example.com",    // Korundu
//   fld_phone: "+90 555 9999999",    // Güncellendi
//   fld_company: "New Corp"          // Eklendi
// }
```

---

### 5. Delete Record

**Endpoint:** `DELETE /api/records/{record_id}`
**Protected:** Evet
**Response:** 204 No Content

#### Example

```javascript
const deleteRecord = async (recordId) => {
  const response = await fetch(`${API_BASE_URL}/api/records/${recordId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error("Record silinemedi");
  return true;
};
```

---

### 6. Search Records

**Endpoint:** `GET /api/records/search?object_id={object_id}&q={query}`
**Protected:** Evet

**IMPORTANT:** `object_id` ve `q` query parametreleri zorunludur!

#### Query Parameters

```typescript
interface RecordSearchParams {
  object_id: string;         // REQUIRED - Object ID
  q: string;                 // REQUIRED - Search query (primary_value'da arar)
  page?: number;             // Sayfa numarası
  page_size?: number;        // Sayfa boyutu
}
```

#### Example

```javascript
const searchRecords = async (objectId, query, page = 1, pageSize = 50) => {
  const params = new URLSearchParams({
    object_id: objectId,
    q: query,
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/records/search?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Arama yapılamadı");
  return await response.json();
};

// Kullanım
const results = await searchRecords("obj_contact", "ali");
// primary_value'da "ali" içeren tüm contact'ları bulur
// Örnek: "ali@example.com", "Ali Veli" vb.
```

---

## Relationships API

Relationship'ler object'ler arası ilişki tanımlarıdır (1:N veya N:N).

### 1. Create Relationship

**Endpoint:** `POST /api/relationships`
**Protected:** Evet

#### Request

```typescript
interface RelationshipCreateRequest {
  name: string;              // Unique identifier (e.g., "contact_opportunity")
  type: "1:N" | "N:N";       // İlişki tipi
  from_object_id: string;    // Kaynak object ID
  to_object_id: string;      // Hedef object ID
  from_label: string;        // Kaynak label (e.g., "Opportunities")
  to_label: string;          // Hedef label (e.g., "Contact")
  description?: string;      // Açıklama
}
```

#### Example

```javascript
const createRelationship = async (relationshipData) => {
  const response = await fetch(`${API_BASE_URL}/api/relationships`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(relationshipData),
  });

  if (!response.ok) throw new Error("Relationship oluşturulamadı");
  return await response.json();
};

// Kullanım - Contact → Opportunity (1:N)
const relationship = await createRelationship({
  name: "contact_opportunity",
  type: "1:N",
  from_object_id: "obj_contact",
  to_object_id: "obj_opportunity",
  from_label: "Opportunities",
  to_label: "Contact",
  description: "Contact has many opportunities",
});

console.log(relationship.id); // "rel_abc12345"
```

#### Response

```json
{
  "id": "rel_abc12345",
  "name": "contact_opportunity",
  "type": "1:N",
  "from_object_id": "obj_contact",
  "to_object_id": "obj_opportunity",
  "from_label": "Opportunities",
  "to_label": "Contact",
  "description": "Contact has many opportunities",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z"
}
```

---

### 2. Get Object Relationships

**Endpoint:** `GET /api/relationships/objects/{object_id}`
**Protected:** Evet

#### Example

```javascript
const getObjectRelationships = async (objectId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/relationships/objects/${objectId}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Relationship'ler alınamadı");
  return await response.json();
};

// Kullanım
const contactRelationships = await getObjectRelationships("obj_contact");
// Contact'ın from_object veya to_object olduğu tüm relationship'leri döner
```

---

### 3. Delete Relationship

**Endpoint:** `DELETE /api/relationships/{relationship_id}`
**Protected:** Evet
**Response:** 204 No Content

**WARNING:** Relationship silindiğinde, ona bağlı tüm relationship_records (record link'leri) de silinir (CASCADE).

#### Example

```javascript
const deleteRelationship = async (relationshipId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/relationships/${relationshipId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) throw new Error("Relationship silinemedi");
  return true;
};
```

---

## Relationship-Records API

Relationship-Records, record'ları relationship üzerinden bağlar (junction table).

### 1. Link Records

**Endpoint:** `POST /api/relationship-records`
**Protected:** Evet

#### Request

```typescript
interface RelationshipRecordCreateRequest {
  relationship_id: string;      // Relationship ID (rel_xxxxxxxx)
  from_record_id: string;       // Kaynak record ID (rec_xxxxxxxx)
  to_record_id: string;         // Hedef record ID (rec_xxxxxxxx)
  relationship_metadata?: {     // İlişkiye özel metadata
    [key: string]: any;
  };
}
```

#### Example

```javascript
const linkRecords = async (linkData) => {
  const response = await fetch(`${API_BASE_URL}/api/relationship-records`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(linkData),
  });

  if (!response.ok) throw new Error("Record'lar bağlanamadı");
  return await response.json();
};

// Kullanım - Ali contact'ını BigDeal opportunity'sine bağla
const link = await linkRecords({
  relationship_id: "rel_contact_opportunity",
  from_record_id: "rec_ali",
  to_record_id: "rec_bigdeal",
  relationship_metadata: {
    role: "Decision Maker",
    influence_level: "High",
  },
});

console.log(link.id); // "lnk_abc12345"
```

#### Response

```json
{
  "id": "lnk_abc12345",
  "relationship_id": "rel_contact_opportunity",
  "from_record_id": "rec_ali",
  "to_record_id": "rec_bigdeal",
  "relationship_metadata": {
    "role": "Decision Maker",
    "influence_level": "High"
  },
  "created_at": "2026-01-18T10:00:00Z",
  "created_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2. Get Related Records

**Endpoint:** `GET /api/relationship-records/records/{record_id}/related?relationship_id={relationship_id}`
**Protected:** Evet

**IMPORTANT:** `relationship_id` query parameter'ı zorunludur!

**NOTE:** Bu endpoint **bidirectional** query yapar (from_record_id VEYA to_record_id eşleşirse döner).

#### Example

```javascript
const getRelatedRecords = async (recordId, relationshipId) => {
  const params = new URLSearchParams({
    relationship_id: relationshipId,
  });

  const response = await fetch(
    `${API_BASE_URL}/api/relationship-records/records/${recordId}/related?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("İlişkili record'lar alınamadı");
  return await response.json();
};

// Kullanım
const aliOpportunities = await getRelatedRecords(
  "rec_ali",
  "rel_contact_opportunity"
);

// Ali'nin bağlı olduğu tüm opportunity'leri döner
// Sonuç:
// [
//   {
//     id: "lnk_abc12345",
//     from_record_id: "rec_ali",
//     to_record_id: "rec_bigdeal",
//     relationship_metadata: { role: "Decision Maker" }
//   },
//   ...
// ]
```

---

### 3. Unlink Records

**Endpoint:** `DELETE /api/relationship-records/{link_id}`
**Protected:** Evet
**Response:** 204 No Content

**NOTE:** Sadece bağlantı silinir, record'ların kendisi silinmez!

#### Example

```javascript
const unlinkRecords = async (linkId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/relationship-records/${linkId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    if (response.status === 404) throw new Error("Link bulunamadı");
    throw new Error("Link silinemedi");
  }

  return true;
};

// Kullanım
await unlinkRecords("lnk_abc12345");
```

---

## Applications API

Application'lar no-code uygulamaları temsil eder (CRM, ITSM vb.).

### 1. Create Application

**Endpoint:** `POST /api/applications`
**Protected:** Evet

#### Request

```typescript
interface ApplicationCreateRequest {
  name: string;              // Unique identifier (e.g., "crm")
  label: string;             // Display name (e.g., "CRM")
  description?: string;      // Açıklama
  icon?: string;             // Icon name
  color?: string;            // Hex color
  is_published?: boolean;    // Yayınlandı mı? (default: false)
  config?: {                 // App konfigürasyonu
    [key: string]: any;
  };
}
```

#### Example

```javascript
const createApplication = async (appData) => {
  const response = await fetch(`${API_BASE_URL}/api/applications`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(appData),
  });

  if (!response.ok) throw new Error("Application oluşturulamadı");
  return await response.json();
};

// Kullanım
const crm = await createApplication({
  name: "crm",
  label: "CRM",
  description: "Customer Relationship Management",
  icon: "briefcase",
  color: "#3B82F6",
  config: {
    modules: ["contacts", "opportunities", "companies"],
  },
});

console.log(crm.id); // "app_abc12345"
```

#### Response

```json
{
  "id": "app_abc12345",
  "name": "crm",
  "label": "CRM",
  "description": "Customer Relationship Management",
  "icon": "briefcase",
  "color": "#3B82F6",
  "is_published": false,
  "config": {
    "modules": ["contacts", "opportunities", "companies"]
  },
  "published_at": null,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-18T10:00:00Z"
}
```

---

### 2. List Applications

**Endpoint:** `GET /api/applications`
**Protected:** Evet

#### Query Parameters

```typescript
interface ApplicationListParams {
  is_published?: boolean;    // Yayınlanmış uygulamaları filtrele
  page?: number;             // Sayfa numarası
  page_size?: number;        // Sayfa boyutu
}
```

#### Example

```javascript
const listApplications = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.is_published !== undefined) {
    params.append("is_published", filters.is_published);
  }
  if (filters.page) params.append("page", filters.page);
  if (filters.page_size) params.append("page_size", filters.page_size);

  const response = await fetch(
    `${API_BASE_URL}/api/applications?${params}`,
    { headers: getAuthHeaders() }
  );

  if (!response.ok) throw new Error("Application'lar alınamadı");
  return await response.json();
};

// Kullanım
const publishedApps = await listApplications({ is_published: true });
const allApps = await listApplications();
```

---

### 3. Publish Application

**Endpoint:** `POST /api/applications/{app_id}/publish`
**Protected:** Evet

#### Example

```javascript
const publishApplication = async (appId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/applications/${appId}/publish`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) throw new Error("Application yayınlanamadı");
  return await response.json();
};

// Kullanım
const published = await publishApplication("app_abc12345");
console.log(published.is_published); // true
console.log(published.published_at); // "2026-01-18T10:00:00Z"
```

---

### 4. Delete Application

**Endpoint:** `DELETE /api/applications/{app_id}`
**Protected:** Evet
**Response:** 204 No Content

#### Example

```javascript
const deleteApplication = async (appId) => {
  const response = await fetch(`${API_BASE_URL}/api/applications/${appId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error("Application silinemedi");
  return true;
};
```

---

## Workflow Örnekleri

### Workflow 1: Contact CRM Oluşturma

```javascript
// 1. Field'ları oluştur
const emailField = await createField({
  name: "email",
  label: "Email",
  type: "email",
  category: "Contact Info",
});

const phoneField = await createField({
  name: "phone",
  label: "Phone",
  type: "phone",
  category: "Contact Info",
});

const companyField = await createField({
  name: "company",
  label: "Company",
  type: "text",
  category: "Contact Info",
});

// 2. Contact object'i oluştur
const contactObject = await createObject({
  name: "contact",
  label: "Contact",
  plural_name: "Contacts",
  category: "CRM",
  icon: "user",
  color: "#3B82F6",
});

// 3. Field'ları object'e ekle (sıralı)
await addFieldToObject({
  object_id: contactObject.id,
  field_id: emailField.id,
  display_order: 0,
  is_required: true,
  is_unique: true,
  is_primary_field: true,
});

await addFieldToObject({
  object_id: contactObject.id,
  field_id: phoneField.id,
  display_order: 1,
  is_required: false,
});

await addFieldToObject({
  object_id: contactObject.id,
  field_id: companyField.id,
  display_order: 2,
  is_required: false,
});

// 4. Contact record'ları oluştur
const ali = await createRecord({
  object_id: contactObject.id,
  data: {
    [emailField.id]: "ali@example.com",
    [phoneField.id]: "+90 555 1234567",
    [companyField.id]: "Acme Corp",
  },
});

const ahmet = await createRecord({
  object_id: contactObject.id,
  data: {
    [emailField.id]: "ahmet@example.com",
    [phoneField.id]: "+90 555 9876543",
    [companyField.id]: "Tech Inc",
  },
});

console.log("CRM oluşturuldu!");
console.log("Contact Object:", contactObject.id);
console.log("Ali:", ali.id);
console.log("Ahmet:", ahmet.id);
```

---

### Workflow 2: Contact → Opportunity İlişkisi

```javascript
// 1. Opportunity object'i oluştur
const opportunityObject = await createObject({
  name: "opportunity",
  label: "Opportunity",
  plural_name: "Opportunities",
  category: "CRM",
  icon: "dollar-sign",
  color: "#10B981",
});

// 2. Opportunity field'larını oluştur ve ekle
const dealNameField = await createField({
  name: "deal_name",
  label: "Deal Name",
  type: "text",
});

const amountField = await createField({
  name: "amount",
  label: "Amount",
  type: "number",
});

await addFieldToObject({
  object_id: opportunityObject.id,
  field_id: dealNameField.id,
  display_order: 0,
  is_primary_field: true,
  is_required: true,
});

await addFieldToObject({
  object_id: opportunityObject.id,
  field_id: amountField.id,
  display_order: 1,
});

// 3. Opportunity record'ları oluştur
const bigDeal = await createRecord({
  object_id: opportunityObject.id,
  data: {
    [dealNameField.id]: "Big Deal",
    [amountField.id]: 100000,
  },
});

const mediumDeal = await createRecord({
  object_id: opportunityObject.id,
  data: {
    [dealNameField.id]: "Medium Deal",
    [amountField.id]: 50000,
  },
});

// 4. Contact → Opportunity relationship tanımla (1:N)
const relationship = await createRelationship({
  name: "contact_opportunity",
  type: "1:N",
  from_object_id: contactObject.id,
  to_object_id: opportunityObject.id,
  from_label: "Opportunities",
  to_label: "Contact",
  description: "Contact has many opportunities",
});

// 5. Record'ları bağla
const link1 = await linkRecords({
  relationship_id: relationship.id,
  from_record_id: ali.id,
  to_record_id: bigDeal.id,
  relationship_metadata: {
    role: "Decision Maker",
    influence_level: "High",
  },
});

const link2 = await linkRecords({
  relationship_id: relationship.id,
  from_record_id: ali.id,
  to_record_id: mediumDeal.id,
  relationship_metadata: {
    role: "Influencer",
    influence_level: "Medium",
  },
});

// 6. Ali'nin tüm opportunity'lerini getir
const aliOpportunities = await getRelatedRecords(ali.id, relationship.id);

console.log(`Ali'nin ${aliOpportunities.length} opportunity'si var`);
// Ali'nin 2 opportunity'si var

// 7. Opportunity detaylarını getir
for (const link of aliOpportunities) {
  const opportunity = await getRecord(link.to_record_id);
  console.log(
    `- ${opportunity.data[dealNameField.id]}: $${opportunity.data[amountField.id]} (Role: ${link.relationship_metadata.role})`
  );
}
// - Big Deal: $100000 (Role: Decision Maker)
// - Medium Deal: $50000 (Role: Influencer)
```

---

### Workflow 3: CRM Application Yayınlama

```javascript
// 1. CRM application oluştur
const crmApp = await createApplication({
  name: "crm",
  label: "CRM",
  description: "Customer Relationship Management",
  icon: "briefcase",
  color: "#3B82F6",
  config: {
    modules: ["contacts", "opportunities"],
    objects: [contactObject.id, opportunityObject.id],
    relationships: [relationship.id],
  },
});

console.log("CRM Application:", crmApp.id);
console.log("Published:", crmApp.is_published); // false

// 2. CRM'i yayınla
const published = await publishApplication(crmApp.id);

console.log("Published:", published.is_published); // true
console.log("Published At:", published.published_at);

// 3. Yayınlanmış uygulamaları listele
const publishedApps = await listApplications({ is_published: true });

console.log(`${publishedApps.length} yayınlanmış uygulama var`);
```

---

## TypeScript Tipleri

### Authentication Types

```typescript
// Request Types
interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

interface LoginRequest {
  username: string; // Email
  password: string;
}

// Response Types
interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

interface LoginResponse {
  access_token: string;
  token_type: "bearer";
}
```

---

### Field Types

```typescript
interface Field {
  id: string;
  name: string;
  label: string;
  type: FieldType;
  category: string | null;
  description: string | null;
  is_system_field: boolean;
  config: Record<string, any>;
  created_by: string;
  created_at: string;
  updated_at: string | null;
}

type FieldType =
  | "text"
  | "email"
  | "phone"
  | "number"
  | "date"
  | "datetime"
  | "textarea"
  | "select"
  | "multiselect"
  | "checkbox"
  | "radio"
  | "url"
  | "file";

interface FieldCreateRequest {
  name: string;
  label: string;
  type: FieldType;
  category?: string;
  description?: string;
  is_system_field?: boolean;
  config?: Record<string, any>;
}

interface FieldUpdateRequest {
  label?: string;
  category?: string;
  description?: string;
  config?: Record<string, any>;
}
```

---

### Object Types

```typescript
interface Object {
  id: string;
  name: string;
  label: string;
  plural_name: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  category: string | null;
  views: Record<string, any> | null;
  permissions: Record<string, any> | null;
  created_by: string;
  created_at: string;
  updated_at: string | null;
}

interface ObjectCreateRequest {
  name: string;
  label: string;
  plural_name: string;
  description?: string;
  icon?: string;
  color?: string;
  category?: string;
  views?: Record<string, any>;
  permissions?: Record<string, any>;
}

interface ObjectUpdateRequest {
  label?: string;
  plural_name?: string;
  description?: string;
  icon?: string;
  color?: string;
  category?: string;
  views?: Record<string, any>;
  permissions?: Record<string, any>;
}
```

---

### Object-Field Types

```typescript
interface ObjectField {
  id: string;
  object_id: string;
  field_id: string;
  display_order: number;
  is_required: boolean;
  is_unique: boolean;
  is_primary_field: boolean;
  default_value: any;
  validation_rules: Record<string, any> | null;
  created_at: string;
  updated_at: string | null;
}

interface ObjectFieldCreateRequest {
  object_id: string;
  field_id: string;
  display_order?: number;
  is_required?: boolean;
  is_unique?: boolean;
  is_primary_field?: boolean;
  default_value?: any;
  validation_rules?: Record<string, any>;
}

interface ObjectFieldUpdateRequest {
  display_order?: number;
  is_required?: boolean;
  is_unique?: boolean;
  is_primary_field?: boolean;
  default_value?: any;
  validation_rules?: Record<string, any>;
}
```

---

### Record Types

```typescript
interface Record {
  id: string;
  object_id: string;
  data: Record<string, any>; // JSONB field values
  primary_value: string;
  created_by: string;
  created_at: string;
  updated_at: string | null;
  updated_by: string | null;
}

interface RecordCreateRequest {
  object_id: string;
  data: Record<string, any>;
  primary_value?: string; // Auto-set from primary field
}

interface RecordUpdateRequest {
  data: Record<string, any>; // MERGE edilir
  primary_value?: string;    // Auto-update
}
```

---

### Relationship Types

```typescript
interface Relationship {
  id: string;
  name: string;
  type: "1:N" | "N:N";
  from_object_id: string;
  to_object_id: string;
  from_label: string;
  to_label: string;
  description: string | null;
  created_by: string;
  created_at: string;
}

interface RelationshipCreateRequest {
  name: string;
  type: "1:N" | "N:N";
  from_object_id: string;
  to_object_id: string;
  from_label: string;
  to_label: string;
  description?: string;
}
```

---

### Relationship-Record Types

```typescript
interface RelationshipRecord {
  id: string;
  relationship_id: string;
  from_record_id: string;
  to_record_id: string;
  relationship_metadata: Record<string, any>;
  created_at: string;
  created_by: string;
}

interface RelationshipRecordCreateRequest {
  relationship_id: string;
  from_record_id: string;
  to_record_id: string;
  relationship_metadata?: Record<string, any>;
}
```

---

### Application Types

```typescript
interface Application {
  id: string;
  name: string;
  label: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  is_published: boolean;
  config: Record<string, any> | null;
  published_at: string | null;
  created_by: string;
  created_at: string;
}

interface ApplicationCreateRequest {
  name: string;
  label: string;
  description?: string;
  icon?: string;
  color?: string;
  is_published?: boolean;
  config?: Record<string, any>;
}
```

---

## Best Practices

### 1. Token Management

```javascript
// ✅ DOĞRU - Token'ı localStorage'da sakla
const login = async (email, password) => {
  const response = await loginAPI(email, password);
  localStorage.setItem("access_token", response.access_token);
  return response;
};

const logout = () => {
  localStorage.removeItem("access_token");
  // Redirect to login page
};

// Token expiry check
const isTokenExpired = () => {
  const token = localStorage.getItem("access_token");
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return Date.now() >= payload.exp * 1000;
  } catch (error) {
    return true;
  }
};

// Auto-refresh veya logout
if (isTokenExpired()) {
  logout();
}
```

---

### 2. Centralized API Client

```javascript
// utils/apiClient.js
class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Not authenticated");
    return {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }

      const error = await response.json();
      throw new Error(error.detail || "API Error");
    }

    // 204 No Content için null dön
    if (response.status === 204) return null;

    return await response.json();
  }

  // GET
  async get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  }

  // POST
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // PATCH
  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  // DELETE
  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
}

// Export singleton
export const apiClient = new APIClient("http://localhost:8000");

// Kullanım
import { apiClient } from "./utils/apiClient";

const fields = await apiClient.get("/api/fields");
const newField = await apiClient.post("/api/fields", {
  name: "email",
  label: "Email",
  type: "email",
});
```

---

### 3. React Hooks

```javascript
// hooks/useAPI.js
import { useState, useEffect } from "react";
import { apiClient } from "../utils/apiClient";

export const useAPI = (endpoint, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiClient.get(endpoint);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error };
};

// Kullanım
const FieldsList = () => {
  const { data: fields, loading, error } = useAPI("/api/fields");

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {fields.map((field) => (
        <li key={field.id}>{field.label}</li>
      ))}
    </ul>
  );
};
```

---

### 4. Error Handling

```javascript
// utils/errorHandler.js
export const handleAPIError = (error) => {
  console.error("API Error:", error);

  if (error.response) {
    // Server response error
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return "Bad request. Please check your input.";
      case 401:
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return "Session expired. Please login again.";
      case 404:
        return "Resource not found.";
      case 422:
        // Validation error
        if (Array.isArray(data.detail)) {
          return data.detail.map((err) => err.msg).join(", ");
        }
        return data.detail || "Validation error.";
      case 500:
        return "Server error. Please try again later.";
      default:
        return data.detail || "An error occurred.";
    }
  }

  // Network error
  if (error.request) {
    return "Network error. Please check your connection.";
  }

  // Other error
  return error.message || "An unexpected error occurred.";
};

// Kullanım
try {
  const field = await createField(data);
} catch (error) {
  const message = handleAPIError(error);
  showNotification(message, "error");
}
```

---

### 5. Pagination Helper

```javascript
// utils/pagination.js
export const usePagination = (fetchFunction, pageSize = 50) => {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const result = await fetchFunction(page, pageSize);

      if (result.length < pageSize) {
        setHasMore(false);
      }

      setData((prev) => [...prev, ...result]);
      setPage((prev) => prev + 1);
    } catch (error) {
      console.error("Pagination error:", error);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData([]);
    setPage(1);
    setHasMore(true);
  };

  return { data, loading, hasMore, loadMore, reset };
};

// Kullanım
const RecordsList = ({ objectId }) => {
  const { data, loading, hasMore, loadMore } = usePagination(
    (page, pageSize) => listRecords(objectId, page, pageSize)
  );

  return (
    <div>
      {data.map((record) => (
        <RecordCard key={record.id} record={record} />
      ))}

      {hasMore && (
        <button onClick={loadMore} disabled={loading}>
          {loading ? "Loading..." : "Load More"}
        </button>
      )}
    </div>
  );
};
```

---

## Error Handling

### HTTP Status Codes

| Status | Açıklama | Ne Zaman Döner |
|--------|----------|----------------|
| 200 | OK | Başarılı GET/PATCH |
| 201 | Created | Başarılı POST |
| 204 | No Content | Başarılı DELETE |
| 400 | Bad Request | İş mantığı hatası |
| 401 | Unauthorized | JWT token eksik/geçersiz |
| 404 | Not Found | Kayıt bulunamadı |
| 422 | Unprocessable Entity | Validation hatası (Pydantic) |
| 500 | Internal Server Error | Server hatası |

---

### Error Response Formats

#### Generic Error (400, 404, 500)

```json
{
  "detail": "Error message here"
}
```

#### Validation Error (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required"
    }
  ]
}
```

#### Unauthorized Error (401)

```json
{
  "detail": "Not authenticated"
}
```

---

### Error Handling Examples

```javascript
// Generic error handler
const handleError = async (response) => {
  if (!response.ok) {
    const error = await response.json();

    if (response.status === 422) {
      // Validation errors
      const errors = error.detail.map((err) => ({
        field: err.loc[err.loc.length - 1],
        message: err.msg,
      }));
      throw { status: 422, errors };
    }

    throw { status: response.status, message: error.detail };
  }

  return response;
};

// Usage
try {
  const response = await fetch(`${API_BASE_URL}/api/fields`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(fieldData),
  });

  await handleError(response);
  const field = await response.json();
  return field;
} catch (error) {
  if (error.status === 422) {
    // Display validation errors
    error.errors.forEach((err) => {
      console.error(`${err.field}: ${err.message}`);
    });
  } else {
    console.error(error.message);
  }
}
```

---

## Common Pitfalls

### ❌ Pitfall 1: Login Endpoint Form Data

```javascript
// ❌ YANLIŞ - JSON gönderme
const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "...", password: "..." }),
});
// 422 Validation Error!

// ✅ DOĞRU - Form data gönder
const formData = new URLSearchParams();
formData.append("username", email); // NOT "email", use "username"!
formData.append("password", password);

const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: formData,
});
```

---

### ❌ Pitfall 2: Missing Query Parameters

```javascript
// ❌ YANLIŞ - object_id eksik
const records = await fetch(`${API_BASE_URL}/api/records`);
// 422 Validation Error: object_id required

// ✅ DOĞRU - object_id ekle
const records = await fetch(
  `${API_BASE_URL}/api/records?object_id=obj_contact`
);
```

---

### ❌ Pitfall 3: Record Update Overwriting

```javascript
// Mevcut data: { fld_email: "ali@example.com", fld_phone: "+90 555..." }

// ❌ YANLIŞ - Tüm data'yı gönderme (MERGE olur ama gereksiz)
await updateRecord("rec_abc", {
  data: {
    fld_email: "ali@example.com",    // Değişmedi ama gönderiliyor
    fld_phone: "+90 555 9999999",    // Değişti
    fld_company: "New Corp",         // Yeni
  },
});

// ✅ DOĞRU - Sadece değişen field'ları gönder (MERGE)
await updateRecord("rec_abc", {
  data: {
    fld_phone: "+90 555 9999999",    // Değişti
    fld_company: "New Corp",         // Yeni
  },
});
// Sonuç: { fld_email: "ali@example.com", fld_phone: "+90 555 9999999", fld_company: "New Corp" }
```

---

### ❌ Pitfall 4: Not Checking 204 No Content

```javascript
// ❌ YANLIŞ - DELETE sonrası JSON parse etme
const response = await fetch(`${API_BASE_URL}/api/fields/${fieldId}`, {
  method: "DELETE",
  headers: getAuthHeaders(),
});

const data = await response.json();
// Error: Unexpected end of JSON input

// ✅ DOĞRU - 204 için null dön
const response = await fetch(`${API_BASE_URL}/api/fields/${fieldId}`, {
  method: "DELETE",
  headers: getAuthHeaders(),
});

if (response.status === 204) {
  return null; // Başarılı, body yok
}

return await response.json();
```

---

### ❌ Pitfall 5: Token Expiry Not Handled

```javascript
// ❌ YANLIŞ - Token expiry kontrol yok
const fields = await fetch(`${API_BASE_URL}/api/fields`, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
  },
});
// 401 Unauthorized (token expired) ama kullanıcı login sayfasına yönlendirilmiyor

// ✅ DOĞRU - 401 durumunda logout ve redirect
const response = await fetch(`${API_BASE_URL}/api/fields`, {
  headers: getAuthHeaders(),
});

if (response.status === 401) {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
  return;
}

return await response.json();
```

---

### ❌ Pitfall 6: Trailing Slash Inconsistency

```javascript
// ❌ POTANSİYEL SORUN - Trailing slash
const response1 = await fetch(`${API_BASE_URL}/api/fields/`);
const response2 = await fetch(`${API_BASE_URL}/api/fields`);

// ✅ DOĞRU - Dual route support (backend destekliyor)
// Her iki şekilde de çalışır ama tutarlı olun
const response = await fetch(`${API_BASE_URL}/api/fields`); // Tercih edilen
```

---

### ❌ Pitfall 7: Not Using Field IDs in Record Data

```javascript
// ❌ YANLIŞ - Field name kullanma
const record = await createRecord({
  object_id: "obj_contact",
  data: {
    email: "ali@example.com", // Field name!
  },
});

// ✅ DOĞRU - Field ID kullan
const record = await createRecord({
  object_id: "obj_contact",
  data: {
    fld_abc12345: "ali@example.com", // Field ID!
  },
});
```

---

### ❌ Pitfall 8: Forgetting Bidirectional Relationship Query

```javascript
// Contact → Opportunity relationship

// ❌ YANLIŞ - Sadece from_record_id'yi kontrol etme
const links = await getRelatedRecords("rec_opportunity", "rel_contact_opportunity");
// Boş array döner çünkü opportunity to_record_id'de

// ✅ DOĞRU - Bidirectional query (backend otomatik yapıyor)
const links = await getRelatedRecords("rec_contact", "rel_contact_opportunity");
// from_record_id veya to_record_id eşleşirse döner
```

---

## Performance Tips

### 1. Use Pagination

```javascript
// ❌ YANLIŞ - Tüm record'ları tek seferde çek
const allRecords = await listRecords("obj_contact", 1, 10000);
// Yavaş! Çok veri

// ✅ DOĞRU - Pagination kullan
const page1 = await listRecords("obj_contact", 1, 50);
const page2 = await listRecords("obj_contact", 2, 50);
```

---

### 2. Parallel Requests

```javascript
// ❌ YANLIŞ - Sequential requests
const fields = await listFields();
const objects = await listObjects();
const applications = await listApplications();
// Toplam: 150ms (50ms * 3)

// ✅ DOĞRU - Parallel requests
const [fields, objects, applications] = await Promise.all([
  listFields(),
  listObjects(),
  listApplications(),
]);
// Toplam: 50ms (paralel)
```

---

### 3. Cache Frequently Used Data

```javascript
// Cache field definitions
const fieldCache = new Map();

const getField = async (fieldId) => {
  if (fieldCache.has(fieldId)) {
    return fieldCache.get(fieldId);
  }

  const field = await apiClient.get(`/api/fields/${fieldId}`);
  fieldCache.set(fieldId, field);
  return field;
};
```

---

## Summary

Bu dokümanda:

1. **Authentication:** Register, Login, Get Current User
2. **Fields API:** Field CRUD, kategori filtreleme
3. **Objects API:** Object CRUD, CASCADE silme
4. **Object-Fields API:** Field'ları object'e bağlama
5. **Records API:** JSONB ile dinamik veri, MERGE update, pagination, search
6. **Relationships API:** Object ilişki tanımları (1:N, N:N)
7. **Relationship-Records API:** Record linking, bidirectional query
8. **Applications API:** No-code app yönetimi, publish
9. **Workflow Örnekleri:** CRM oluşturma, ilişki kurma
10. **TypeScript Tipleri:** Tüm API response/request tipleri
11. **Best Practices:** Token yönetimi, centralized API client, React hooks
12. **Error Handling:** HTTP status codes, validation errors
13. **Common Pitfalls:** Sık yapılan hatalar ve çözümleri

---

**Backend URL:** `http://localhost:8000`
**Docs:** `http://localhost:8000/docs`
**Total Endpoints:** 34
**Version:** v1.0.0

**Sorular için:** [Backend Architecture](../../BACKEND_ARCHITECTURE_ANALYSIS.md) ve [API Index](00-API-DOCUMENTATION-INDEX.md) dökümanlarına bakın.
