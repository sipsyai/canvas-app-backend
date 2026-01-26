# Frontend Requirements Analysis - Canvas App
**Date:** 2026-01-22
**Backend Status:** ✅ Tamamen Hazır
**Purpose:** Backend analizlerine göre frontend gereksinimlerini belirlemek

---

## Executive Summary

Backend **tamamen hazır** ve production-ready durumda. FastAPI + PostgreSQL + JSONB Hybrid Model kullanılarak no-code platform backend'i tamamlanmış. Şimdi frontend'in bu backend ile çalışacak şekilde geliştirilmesi gerekiyor.

**Backend Özellikleri:**
- ✅ 34 API endpoint (CRUD + ilişkiler + arama)
- ✅ JWT authentication
- ✅ JSONB ile dinamik field storage
- ✅ Field Library (merkezi field yönetimi)
- ✅ Object-Field mapping (N:N)
- ✅ Relationships (1:N, N:N)
- ✅ Multi-tenancy (RLS)
- ✅ Pagination, search, filters

---

## 1. Technology Stack (Önerilen)

### Core Framework
```yaml
Framework: React 19
Build Tool: Vite 6.0
Language: TypeScript 5.7
Styling: TailwindCSS 3.4
```

### State Management
```yaml
Option 1: Zustand (önerilen - basit, performanslı)
Option 2: Custom hooks + Context (minimal state için)
```

### Routing
```yaml
React Router: v6 (nested routes + protected routes)
```

### HTTP Client
```yaml
Axios: v1.6+ (interceptors + token management)
```

### UI Components
```yaml
Headless UI: @headlessui/react (accessible components)
Lucide React: lucide-react (modern icons)
React Hook Form: Form validation
```

### Data Fetching
```yaml
TanStack Query: @tanstack/react-query (caching + auto-refetch)
```

---

## 2. Frontend Architecture

### Project Structure

```
src/
├── api/                         # API client ve servisler
│   ├── client.ts                # Axios instance (interceptors)
│   ├── auth.ts                  # Authentication API
│   ├── fields.ts                # Fields API
│   ├── objects.ts               # Objects API
│   ├── records.ts               # Records API
│   ├── relationships.ts         # Relationships API
│   └── applications.ts          # Applications API
│
├── components/                  # Reusable components
│   ├── common/                  # Generic components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   └── Pagination.tsx
│   │
│   ├── fields/                  # Field components
│   │   ├── FieldLibrary.tsx     # Field library UI
│   │   ├── FieldCard.tsx        # Field display card
│   │   ├── FieldForm.tsx        # Create/edit field form
│   │   └── FieldTypePicker.tsx  # Field type selector
│   │
│   ├── objects/                 # Object components
│   │   ├── ObjectBuilder.tsx    # Object builder UI
│   │   ├── ObjectCard.tsx
│   │   ├── ObjectFieldMapper.tsx # Drag-drop field assignment
│   │   └── ViewConfigurator.tsx # Table/form/kanban view config
│   │
│   ├── records/                 # Record components
│   │   ├── RecordTable.tsx      # Table view (list)
│   │   ├── RecordForm.tsx       # Form view (detail/edit)
│   │   ├── RecordKanban.tsx     # Kanban view
│   │   ├── RecordCalendar.tsx   # Calendar view
│   │   └── RecordDetail.tsx     # Multi-view detail page
│   │
│   ├── relationships/           # Relationship components
│   │   ├── RelationshipBuilder.tsx
│   │   ├── RelatedRecordsList.tsx
│   │   └── LinkRecordsModal.tsx
│   │
│   └── applications/            # Application components
│       ├── AppBuilder.tsx
│       ├── AppNavigation.tsx
│       └── AppPublisher.tsx
│
├── hooks/                       # Custom hooks
│   ├── useAuth.ts               # Authentication hook
│   ├── useFields.ts             # Fields data hook
│   ├── useObjects.ts            # Objects data hook
│   ├── useRecords.ts            # Records data hook
│   ├── usePagination.ts         # Pagination logic
│   └── useRelationships.ts      # Relationships hook
│
├── pages/                       # Page components
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   │
│   ├── fields/
│   │   ├── FieldLibraryPage.tsx
│   │   └── FieldDetailPage.tsx
│   │
│   ├── objects/
│   │   ├── ObjectListPage.tsx
│   │   ├── ObjectBuilderPage.tsx
│   │   └── ObjectDetailPage.tsx
│   │
│   ├── records/
│   │   ├── RecordListPage.tsx
│   │   └── RecordDetailPage.tsx
│   │
│   └── applications/
│       ├── AppListPage.tsx
│       └── AppBuilderPage.tsx
│
├── stores/                      # Zustand stores (if using)
│   ├── authStore.ts
│   ├── fieldStore.ts
│   ├── objectStore.ts
│   └── recordStore.ts
│
├── types/                       # TypeScript types
│   ├── api.ts                   # API response/request types
│   ├── field.ts                 # Field types
│   ├── object.ts                # Object types
│   ├── record.ts                # Record types
│   └── relationship.ts          # Relationship types
│
├── utils/                       # Helper functions
│   ├── jsonb.ts                 # JSONB helpers
│   ├── validation.ts            # Form validation
│   ├── formatting.ts            # Date/currency/phone formatting
│   └── fieldRenderers.ts        # Dynamic field rendering
│
├── App.tsx                      # Main app component
├── main.tsx                     # Entry point
└── router.tsx                   # Route configuration
```

---

## 3. Core Modules (Detaylı)

### 3.1 Authentication Module

#### Features
- ✅ Login form (email + password)
- ✅ Register form (email + password + full_name)
- ✅ JWT token storage (localStorage)
- ✅ Auto-logout on token expiry
- ✅ Protected routes
- ✅ Current user context

#### Components

**LoginPage.tsx**
```typescript
// src/pages/auth/LoginPage.tsx
import { useAuth } from '@/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (email: string, password: string) => {
    await login(email, password);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit}>
        {/* Email input */}
        {/* Password input */}
        {/* Submit button */}
        {error && <div className="text-red-500">{error}</div>}
      </form>
    </div>
  );
}
```

**useAuth Hook**
```typescript
// src/hooks/useAuth.ts
import { create } from 'zustand';
import { login as loginAPI, getCurrentUser } from '@/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const { access_token } = await loginAPI(email, password);
      localStorage.setItem('access_token', access_token);

      const user = await getCurrentUser();
      set({ token: access_token, user, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const user = await getCurrentUser();
      set({ user, token });
    } catch (error) {
      // Token invalid
      localStorage.removeItem('access_token');
      set({ user: null, token: null });
    }
  },
}));
```

**Protected Route**
```typescript
// src/components/auth/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/hooks/useAuth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();

  if (!token) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
}
```

---

### 3.2 Field Library Module

#### Features
- ✅ Field CRUD (Create, Read, Update, Delete)
- ✅ Field categories (Contact Info, Business, System)
- ✅ Field types (text, email, phone, number, date, select, etc.)
- ✅ Field search & filter
- ✅ Reusable field components

#### Components

**FieldLibraryPage.tsx**
```typescript
// src/pages/fields/FieldLibraryPage.tsx
import { useFields } from '@/hooks/useFields';
import { FieldCard } from '@/components/fields/FieldCard';
import { FieldForm } from '@/components/fields/FieldForm';

export default function FieldLibraryPage() {
  const { fields, loading, createField, deleteField } = useFields();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleCreateField = async (fieldData: FieldCreateRequest) => {
    await createField(fieldData);
    setIsCreateModalOpen(false);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Field Library</h1>
        <button onClick={() => setIsCreateModalOpen(true)}>
          + New Field
        </button>
      </div>

      {/* Category tabs */}
      <div className="flex gap-2 mb-6">
        <button>All</button>
        <button>Contact Info</button>
        <button>Business</button>
        <button>System</button>
      </div>

      {/* Field grid */}
      <div className="grid grid-cols-3 gap-4">
        {fields.map((field) => (
          <FieldCard
            key={field.id}
            field={field}
            onDelete={() => deleteField(field.id)}
          />
        ))}
      </div>

      {/* Create modal */}
      {isCreateModalOpen && (
        <FieldForm
          onSubmit={handleCreateField}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      )}
    </div>
  );
}
```

**FieldCard.tsx**
```typescript
// src/components/fields/FieldCard.tsx
interface FieldCardProps {
  field: Field;
  onDelete: () => void;
}

export function FieldCard({ field, onDelete }: FieldCardProps) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-lg transition">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold">{field.label}</h3>
          <p className="text-sm text-gray-500">{field.name}</p>
        </div>
        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
          {field.type}
        </span>
      </div>

      {field.category && (
        <p className="text-xs text-gray-400 mt-2">{field.category}</p>
      )}

      <div className="mt-4 flex gap-2">
        <button className="text-sm text-blue-600">Edit</button>
        <button className="text-sm text-red-600" onClick={onDelete}>
          Delete
        </button>
      </div>
    </div>
  );
}
```

**useFields Hook**
```typescript
// src/hooks/useFields.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listFields, createField as createFieldAPI, deleteField as deleteFieldAPI } from '@/api/fields';

export function useFields(filters?: { category?: string; is_system?: boolean }) {
  const queryClient = useQueryClient();

  const { data: fields = [], isLoading } = useQuery({
    queryKey: ['fields', filters],
    queryFn: () => listFields(filters),
  });

  const createMutation = useMutation({
    mutationFn: createFieldAPI,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteFieldAPI,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });

  return {
    fields,
    loading: isLoading,
    createField: createMutation.mutateAsync,
    deleteField: deleteMutation.mutateAsync,
  };
}
```

---

### 3.3 Object Builder Module

#### Features
- ✅ Object CRUD
- ✅ Field assignment (drag-drop veya multi-select)
- ✅ Field ordering (display_order)
- ✅ Required/unique/primary field settings
- ✅ View configurator (form, table, kanban, calendar)
- ✅ Icon & color picker

#### Components

**ObjectBuilderPage.tsx**
```typescript
// src/pages/objects/ObjectBuilderPage.tsx
export default function ObjectBuilderPage() {
  const [step, setStep] = useState<'basic' | 'fields' | 'views'>('basic');
  const [objectData, setObjectData] = useState<Partial<Object>>({});

  return (
    <div className="p-6">
      {/* Step indicator */}
      <div className="flex gap-4 mb-6">
        <div className={step === 'basic' ? 'font-bold' : ''}>1. Basic Info</div>
        <div className={step === 'fields' ? 'font-bold' : ''}>2. Fields</div>
        <div className={step === 'views' ? 'font-bold' : ''}>3. Views</div>
      </div>

      {/* Step content */}
      {step === 'basic' && (
        <ObjectBasicForm
          data={objectData}
          onChange={setObjectData}
          onNext={() => setStep('fields')}
        />
      )}

      {step === 'fields' && (
        <ObjectFieldMapper
          objectId={objectData.id}
          onNext={() => setStep('views')}
          onBack={() => setStep('basic')}
        />
      )}

      {step === 'views' && (
        <ViewConfigurator
          objectId={objectData.id}
          onSave={() => navigate('/objects')}
          onBack={() => setStep('fields')}
        />
      )}
    </div>
  );
}
```

**ObjectFieldMapper.tsx (Critical Component)**
```typescript
// src/components/objects/ObjectFieldMapper.tsx
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { useFields } from '@/hooks/useFields';
import { useObjectFields } from '@/hooks/useObjectFields';

interface ObjectFieldMapperProps {
  objectId: string;
  onNext: () => void;
  onBack: () => void;
}

export function ObjectFieldMapper({ objectId, onNext, onBack }: ObjectFieldMapperProps) {
  const { fields: availableFields } = useFields();
  const { objectFields, addField, removeField, updateFieldOrder } = useObjectFields(objectId);

  const handleDragEnd = (result) => {
    if (!result.destination) return;
    updateFieldOrder(result.source.index, result.destination.index);
  };

  const handleAddField = async (fieldId: string) => {
    await addField({
      object_id: objectId,
      field_id: fieldId,
      display_order: objectFields.length,
      is_required: false,
    });
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Available fields */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Available Fields</h2>
        <div className="space-y-2">
          {availableFields.map((field) => (
            <div
              key={field.id}
              className="p-3 border rounded flex justify-between items-center"
            >
              <div>
                <p className="font-medium">{field.label}</p>
                <p className="text-sm text-gray-500">{field.type}</p>
              </div>
              <button
                onClick={() => handleAddField(field.id)}
                className="text-blue-600 hover:text-blue-800"
              >
                + Add
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Selected fields (drag-drop) */}
      <div>
        <h2 className="text-lg font-semibold mb-4">
          Object Fields ({objectFields.length})
        </h2>
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="object-fields">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className="space-y-2"
              >
                {objectFields.map((objectField, index) => (
                  <Draggable
                    key={objectField.id}
                    draggableId={objectField.id}
                    index={index}
                  >
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="p-3 border rounded bg-white shadow-sm"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-medium">{objectField.field.label}</p>
                            <div className="flex gap-2 mt-1">
                              <label>
                                <input
                                  type="checkbox"
                                  checked={objectField.is_required}
                                  onChange={(e) =>
                                    updateField(objectField.id, {
                                      is_required: e.target.checked,
                                    })
                                  }
                                />
                                Required
                              </label>
                              <label>
                                <input
                                  type="checkbox"
                                  checked={objectField.is_primary_field}
                                  onChange={(e) =>
                                    updateField(objectField.id, {
                                      is_primary_field: e.target.checked,
                                    })
                                  }
                                />
                                Primary
                              </label>
                            </div>
                          </div>
                          <button
                            onClick={() => removeField(objectField.id)}
                            className="text-red-600"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        <div className="mt-6 flex justify-between">
          <button onClick={onBack}>Back</button>
          <button onClick={onNext}>Next: Configure Views</button>
        </div>
      </div>
    </div>
  );
}
```

---

### 3.4 Record Views Module

#### Features
- ✅ Table View (data grid with pagination)
- ✅ Form View (create/edit with dynamic fields)
- ✅ Kanban View (stage-based grouping)
- ✅ Calendar View (date-based display)
- ✅ Detail page with multi-view tabs

#### Components

**RecordTable.tsx (Critical)**
```typescript
// src/components/records/RecordTable.tsx
import { useRecords } from '@/hooks/useRecords';
import { usePagination } from '@/hooks/usePagination';

interface RecordTableProps {
  objectId: string;
}

export function RecordTable({ objectId }: RecordTableProps) {
  const { page, pageSize, setPage } = usePagination();
  const { records, loading, totalPages } = useRecords(objectId, page, pageSize);
  const { objectFields } = useObjectFields(objectId);

  return (
    <div>
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            {objectFields.map((objectField) => (
              <th key={objectField.id} className="px-6 py-3 text-left">
                {objectField.field.label}
                {objectField.is_required && (
                  <span className="text-red-500">*</span>
                )}
              </th>
            ))}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => (
            <tr key={record.id} className="hover:bg-gray-50">
              {objectFields.map((objectField) => (
                <td key={objectField.id} className="px-6 py-4">
                  {renderFieldValue(
                    record.data[objectField.field_id],
                    objectField.field.type
                  )}
                </td>
              ))}
              <td className="px-6 py-4">
                <button>Edit</button>
                <button>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
}
```

**RecordForm.tsx (Dynamic Field Rendering)**
```typescript
// src/components/records/RecordForm.tsx
import { useForm } from 'react-hook-form';
import { renderFieldInput } from '@/utils/fieldRenderers';

interface RecordFormProps {
  objectId: string;
  recordId?: string; // undefined = create mode
  onSave: (data: Record) => void;
  onCancel: () => void;
}

export function RecordForm({ objectId, recordId, onSave, onCancel }: RecordFormProps) {
  const { objectFields } = useObjectFields(objectId);
  const { record } = useRecord(recordId);
  const { register, handleSubmit, errors } = useForm({
    defaultValues: record?.data || {},
  });

  const onSubmit = async (formData: Record<string, any>) => {
    const recordData = {
      object_id: objectId,
      data: objectFields.reduce((acc, objectField) => {
        acc[objectField.field_id] = formData[objectField.field_id];
        return acc;
      }, {} as Record<string, any>),
    };

    if (recordId) {
      await updateRecord(recordId, recordData);
    } else {
      await createRecord(recordData);
    }

    onSave();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {objectFields.map((objectField) => (
        <div key={objectField.id}>
          <label className="block text-sm font-medium mb-2">
            {objectField.field.label}
            {objectField.is_required && <span className="text-red-500">*</span>}
          </label>

          {renderFieldInput(objectField.field, register, errors)}

          {errors[objectField.field_id] && (
            <p className="text-red-500 text-sm mt-1">
              {errors[objectField.field_id]?.message}
            </p>
          )}
        </div>
      ))}

      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit">
          {recordId ? 'Update' : 'Create'}
        </button>
      </div>
    </form>
  );
}
```

**fieldRenderers.ts (Dynamic Field Input)**
```typescript
// src/utils/fieldRenderers.ts
export function renderFieldInput(
  field: Field,
  register: UseFormRegister,
  errors: FieldErrors
) {
  const commonProps = {
    ...register(field.id, {
      required: field.is_required ? `${field.label} is required` : false,
    }),
    placeholder: field.config?.placeholder,
  };

  switch (field.type) {
    case 'text':
      return <input type="text" {...commonProps} />;

    case 'email':
      return (
        <input
          type="email"
          {...commonProps}
          pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
        />
      );

    case 'phone':
      return <input type="tel" {...commonProps} />;

    case 'number':
      return (
        <input
          type="number"
          {...commonProps}
          min={field.config?.min}
          max={field.config?.max}
        />
      );

    case 'date':
      return <input type="date" {...commonProps} />;

    case 'datetime':
      return <input type="datetime-local" {...commonProps} />;

    case 'textarea':
      return <textarea {...commonProps} rows={4} />;

    case 'select':
      return (
        <select {...commonProps}>
          <option value="">Select...</option>
          {field.config?.options?.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      );

    case 'checkbox':
      return <input type="checkbox" {...commonProps} />;

    case 'url':
      return <input type="url" {...commonProps} />;

    default:
      return <input type="text" {...commonProps} />;
  }
}

export function renderFieldValue(value: any, fieldType: string) {
  if (value === null || value === undefined) return '-';

  switch (fieldType) {
    case 'date':
      return new Date(value).toLocaleDateString();

    case 'datetime':
      return new Date(value).toLocaleString();

    case 'number':
      return Number(value).toLocaleString();

    case 'checkbox':
      return value ? '✓' : '✗';

    case 'url':
      return (
        <a href={value} target="_blank" rel="noopener noreferrer">
          {value}
        </a>
      );

    default:
      return value;
  }
}
```

---

### 3.5 Detail Page (Multi-view) Module

#### Features
- ✅ Overview tab (form view)
- ✅ Related lists tabs (bidirectional relationships)
- ✅ Inline editing
- ✅ Tab navigation

**RecordDetailPage.tsx**
```typescript
// src/pages/records/RecordDetailPage.tsx
export default function RecordDetailPage() {
  const { objectId, recordId } = useParams();
  const [activeTab, setActiveTab] = useState('overview');
  const { record } = useRecord(recordId);
  const { relationships } = useRelationships(objectId);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    ...relationships.map((rel) => ({
      id: `rel_${rel.id}`,
      label: rel.from_label,
    })),
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{record.primary_value}</h1>
        <button>Edit</button>
      </div>

      {/* Tabs */}
      <div className="border-b mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={activeTab === tab.id ? 'border-b-2 border-blue-600' : ''}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'overview' && (
        <RecordOverview record={record} objectId={objectId} />
      )}

      {activeTab.startsWith('rel_') && (
        <RelatedRecordsList
          recordId={recordId}
          relationshipId={activeTab.replace('rel_', '')}
        />
      )}
    </div>
  );
}
```

---

### 3.6 Relationship Manager Module

#### Features
- ✅ Create relationships (1:N, N:N)
- ✅ Link/unlink records
- ✅ Bidirectional display
- ✅ Relationship metadata (role, influence, etc.)

**LinkRecordsModal.tsx**
```typescript
// src/components/relationships/LinkRecordsModal.tsx
export function LinkRecordsModal({
  fromRecordId,
  relationshipId,
  onClose,
}: LinkRecordsModalProps) {
  const { relationship } = useRelationship(relationshipId);
  const { records: targetRecords } = useRecords(relationship.to_object_id);
  const [selectedRecordId, setSelectedRecordId] = useState('');
  const [metadata, setMetadata] = useState<Record<string, any>>({});

  const handleLink = async () => {
    await linkRecords({
      relationship_id: relationshipId,
      from_record_id: fromRecordId,
      to_record_id: selectedRecordId,
      relationship_metadata: metadata,
    });
    onClose();
  };

  return (
    <Modal onClose={onClose}>
      <h2>Link Records</h2>

      {/* Target record selector */}
      <select
        value={selectedRecordId}
        onChange={(e) => setSelectedRecordId(e.target.value)}
      >
        <option value="">Select...</option>
        {targetRecords.map((record) => (
          <option key={record.id} value={record.id}>
            {record.primary_value}
          </option>
        ))}
      </select>

      {/* Metadata inputs (e.g., role, influence) */}
      <input
        placeholder="Role (e.g., Decision Maker)"
        value={metadata.role || ''}
        onChange={(e) => setMetadata({ ...metadata, role: e.target.value })}
      />

      <button onClick={handleLink}>Link</button>
    </Modal>
  );
}
```

---

## 4. API Client Implementation

**client.ts**
```typescript
// src/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add JWT token)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle 401 errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## 5. TypeScript Types

**types/api.ts**
```typescript
// src/types/api.ts
export interface Field {
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

export type FieldType =
  | 'text'
  | 'email'
  | 'phone'
  | 'number'
  | 'date'
  | 'datetime'
  | 'textarea'
  | 'select'
  | 'multiselect'
  | 'checkbox'
  | 'radio'
  | 'url'
  | 'file';

export interface Object {
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

export interface ObjectField {
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

export interface Record {
  id: string;
  object_id: string;
  data: Record<string, any>; // JSONB field values
  primary_value: string;
  created_by: string;
  created_at: string;
  updated_at: string | null;
  updated_by: string | null;
}

export interface Relationship {
  id: string;
  name: string;
  type: '1:N' | 'N:N';
  from_object_id: string;
  to_object_id: string;
  from_label: string;
  to_label: string;
  description: string | null;
  created_by: string;
  created_at: string;
}

export interface RelationshipRecord {
  id: string;
  relationship_id: string;
  from_record_id: string;
  to_record_id: string;
  relationship_metadata: Record<string, any>;
  created_at: string;
  created_by: string;
}

export interface Application {
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
```

---

## 6. Development Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Setup Vite + React + TypeScript
- ✅ Setup TailwindCSS
- ✅ API client with interceptors
- ✅ Authentication module (login, register, protected routes)
- ✅ Basic routing structure

### Phase 2: Field & Object Builder (Week 3-4)
- ✅ Field Library UI
- ✅ Field CRUD operations
- ✅ Object Builder UI
- ✅ Object-Field mapping (drag-drop)
- ✅ Field ordering & settings

### Phase 3: Record Views (Week 5-6)
- ✅ Table View (with pagination)
- ✅ Form View (dynamic field rendering)
- ✅ Record CRUD operations
- ✅ Search & filters

### Phase 4: Detail Page & Relationships (Week 7-8)
- ✅ Detail page with tabs
- ✅ Relationship builder
- ✅ Link/unlink records
- ✅ Related lists display

### Phase 5: Advanced Views (Week 9-10)
- ✅ Kanban View
- ✅ Calendar View
- ✅ Bulk operations
- ✅ Import/Export

### Phase 6: Application Builder (Week 11-12)
- ✅ Application CRUD
- ✅ Navigation menu builder
- ✅ Publish workflow
- ✅ Dashboard

### Phase 7: Polish & Testing (Week 13-14)
- ✅ Error handling improvements
- ✅ Loading states
- ✅ Empty states
- ✅ Responsive design
- ✅ E2E testing

---

## 7. Key Features Summary

### ✅ Zorunlu Özellikler
1. **Authentication** - JWT token yönetimi
2. **Field Library** - Merkezi field yönetimi
3. **Object Builder** - Object oluşturma + field mapping
4. **Record Table** - Pagination ile liste görünümü
5. **Record Form** - Dynamic field rendering
6. **Detail Page** - Multi-view tabs
7. **Relationships** - Link/unlink records
8. **Related Lists** - Bidirectional display

### 🎯 Önerilen Özellikler
9. **Kanban View** - Stage-based grouping
10. **Calendar View** - Date-based display
11. **Search & Filters** - Advanced filtering
12. **Bulk Operations** - Multi-select actions
13. **Import/Export** - CSV/JSON support
14. **Application Builder** - Navigation menu
15. **Real-time Updates** - WebSocket integration

---

## 8. Success Criteria

Frontend başarılı sayılır eğer:
- ✅ Tüm 34 API endpoint kullanılabiliyorsa
- ✅ CRUD operations sorunsuz çalışıyorsa
- ✅ Dynamic form generation field tiplerini destekliyorsa
- ✅ Pagination ve search çalışıyorsa
- ✅ Relationship linking/unlinking çalışıyorsa
- ✅ Detail page tabs doğru data gösteriyorsa
- ✅ Token expiry düzgün handle ediliyorsa
- ✅ Responsive design çalışıyorsa
- ✅ Error states user-friendly ise

---

## 9. Next Steps

1. **Proje Setup** - Vite + React + TypeScript + TailwindCSS
2. **API Client** - Axios + interceptors
3. **Authentication** - Login/register + protected routes
4. **Field Library** - CRUD + category filters
5. **Object Builder** - Field mapping + drag-drop
6. **Record Views** - Table + form + detail page
7. **Relationships** - Link/unlink + related lists

**Estimated Time:** 12-14 weeks (full-time developer)

---

**Bu döküman backend analizlerine göre hazırlanmıştır. Backend tamamen hazır ve production-ready durumda. Frontend bu spesifikasyona göre geliştirilebilir.**
