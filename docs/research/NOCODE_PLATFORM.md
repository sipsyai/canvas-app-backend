# No-Code/Low-Code Platform Architecture Research & Analysis

**Date:** 17 Ocak 2026
**Purpose:** Platform mimarisi için doğru yaklaşımı belirlemek
**Status:** ⚠️ CRITICAL - Mevcut yaklaşım yanlış, yeniden tasarım gerekli

---

## Executive Summary (Türkçe)

### Temel Bulgu: Yanlış Mimarı ile İlerliyoruz

**Mevcut Durum:**
- Uygulama template-centric (form odaklı) bir yaklaşım kullanıyor
- Kullanıcı "bir form tasarlıyor" ve sonra table/kanban görünümleri auto-generate ediliyor
- Bu yaklaşım **sadece basit form-based uygulamalar** için geçerli
- CRM, ITSM, ERP gibi karmaşık uygulamalar inşa edilemiyor

**Doğru Yaklaşım (Tüm Büyük Platformlar):**
- **Object-centric (varlık odaklı)** mimari
- Kullanıcı önce "Object/Table/Entity" oluşturuyor (örn: Contact, Company, Ticket)
- Sonra bu object'ler arasında **relationships** tanımlıyor (1:N, N:N, Lookup, Master-Detail)
- Son olarak her object için **multiple views** oluşturuyor (Form, Table, Kanban, Calendar, Gallery)
- Application = Related Objects'in collection'ı

### Kritik Insight: "Bir Uygulama Tasarlayacak Bir Yapıda Değiliz"

**Şu an yapabildiğimiz:**
```
User → "Müşteri Formu" tasarla → Form fields ekle → Table/Kanban otomatik oluşsun → Bitti
```

**Yapamadığımız (ama yapılması gereken):**
```
User → "CRM Application" oluştur
     → "Contact" object'i ekle (fields: name, email, phone)
     → "Company" object'i ekle (fields: name, industry, revenue)
     → "Opportunity" object'i ekle (fields: title, amount, stage)
     → Relationships tanımla:
        - Contact → Company (N:1 Lookup: "A contact works for a company")
        - Opportunity → Contact (N:1 Lookup: "An opportunity is owned by a contact")
        - Opportunity → Company (N:1 Lookup: "An opportunity is with a company")
     → Her object için views oluştur:
        - Contact: Form, Table, Kanban (by company), Calendar (by created_at)
        - Company: Form, Table, Gallery view
        - Opportunity: Form, Kanban (by stage), Table with filters
```

### Platform Comparison: Hepsi Object-Centric

| Platform | Primary Building Block | Relationship Support | Multi-View | Use Case |
|----------|------------------------|---------------------|-----------|----------|
| **ServiceNow** | Table (Object) | ✅ Reference, Dependent | ✅ Form, List, Related Lists | Enterprise ITSM/Workflow |
| **Airtable** | Table (Base) | ✅ Linked Records, Lookup | ✅ Grid, Form, Kanban, Gallery, Calendar | SMB Collaboration |
| **Salesforce** | Object (sObject) | ✅ Lookup, Master-Detail, Junction | ✅ Form, List, Kanban, Calendar | Enterprise CRM |
| **HubSpot** | Custom Object | ✅ Associations (1:N, N:N) | ✅ Record, Table, Board | SMB CRM/Marketing |
| **Dataverse** | Table (Entity) | ✅ Lookup, 1:N, N:N | ✅ Form, View, Dashboard | Low-code Power Platform |

**Ortak Patern:**
```
Object Definition → Relationships → Views → Data
     ↓                  ↓              ↓       ↓
  Fields            Lookup/Link     Form    Records
  Validation        Master-Detail   Table   CRUD Ops
  Business Rules    Many-to-Many    Kanban  Permissions
```

---

## Platform Comparison Matrix

### Detailed Platform Analysis

#### 1. ServiceNow (Enterprise ITSM/Workflow Leader)

**Focus:** Enterprise IT Service Management, Workflow Automation
**Architecture:** Table-centric (everything is a table/object)
**Complexity:** High (developer-friendly, requires training)
**Best Use Case:** Large enterprise ITSM, ITOM, HR workflows

**Core Architecture:**
```
Workspace (Instance)
  └── Application (e.g., "Incident Management")
       └── Tables (Objects)
            ├── Incident Table
            │    ├── Fields (number, short_description, priority, state, assigned_to)
            │    ├── Relationships
            │    │    ├── Reference to User (assigned_to)
            │    │    ├── Reference to Configuration Item (affected_ci)
            │    │    └── Dependent on Problem (parent_problem)
            │    ├── Business Rules (auto-assign, SLA calculation)
            │    ├── Views
            │    │    ├── Incident Form
            │    │    ├── My Open Incidents (List view with filter)
            │    │    └── Related Incidents (Related List)
            │    └── Data (actual incident records)
            ├── Problem Table
            ├── Change Request Table
            └── Configuration Item Table
```

**Object Model:**
- **Base Table:** `sys_db_object` (metadata for all tables)
- **Field Definition:** `sys_dictionary` (field metadata, validation)
- **Relationship Types:**
  - **Reference:** 1:N lookup (e.g., Incident → Assigned User)
  - **Dependent:** 1:N with cascade delete (e.g., Problem → Child Incidents)
  - **Many-to-Many:** Via junction tables (e.g., Users ↔ Groups)

**Relationship System:**
```javascript
// Example: Incident has Reference to User (assigned_to)
{
  table: 'incident',
  field: 'assigned_to',
  type: 'reference',
  reference_to: 'sys_user',
  on_delete: 'SET NULL' // or 'CASCADE', 'RESTRICT'
}

// Example: Problem has Dependent Incidents
{
  table: 'incident',
  field: 'parent_problem',
  type: 'reference',
  reference_to: 'problem',
  dependent: true, // Incidents deleted when Problem deleted
  relationship_type: '1:N'
}
```

**View System:**
- **Forms:** UI Policy controls field visibility, Client Scripts for validation
- **Lists:** Filtered, sorted tables with columns, inline editing
- **Related Lists:** Shows related records (e.g., "Incidents for this User")
- **Dashboards:** Performance Analytics, Report widgets

**2026 Trends:**
- AI-powered field suggestions (Virtual Agent)
- Auto-relationship detection (suggests relationships based on field names)
- Low-code App Engine Studio (visual interface for creating tables/workflows)

---

#### 2. Airtable (Spreadsheet-Database Hybrid)

**Focus:** Collaborative database for teams
**Architecture:** Base → Table → Records (spreadsheet-like)
**Complexity:** Low (user-friendly, no coding needed)
**Best Use Case:** Project management, content calendars, SMB CRM

**Core Architecture:**
```
Workspace
  └── Base (e.g., "Product Launch Campaign")
       └── Tables
            ├── Tasks Table
            │    ├── Fields (Name, Status, Assignee, Due Date)
            │    ├── Linked Records
            │    │    ├── Link to Team Members (N:N)
            │    │    └── Link to Projects (N:1)
            │    ├── Formulas & Rollups
            │    │    ├── DAYS_REMAINING = DATETIME_DIFF(Due Date, TODAY())
            │    │    └── TOTAL_BUDGET = ROLLUP(Linked Projects, Budget, SUM)
            │    ├── Views
            │    │    ├── Grid (spreadsheet)
            │    │    ├── Kanban (by Status)
            │    │    ├── Calendar (by Due Date)
            │    │    ├── Gallery (image-heavy tasks)
            │    │    └── Form (for task submission)
            │    └── Data (task records)
            ├── Team Members Table
            ├── Projects Table
            └── Assets Table
```

**Object Model:**
- **Table:** No explicit schema definition, fields added dynamically
- **Field Types:** 30+ types (Text, Number, Date, Attachment, Linked Record, Lookup, Rollup, Formula, etc.)
- **Primary Key:** Auto-generated `record_id`

**Relationship System:**
```javascript
// Example: Tasks linked to Team Members (N:N)
{
  table: 'Tasks',
  field: 'Assigned To',
  type: 'multipleRecordLinks',
  linked_table: 'Team Members',
  relationship: 'N:N',
  allow_multiple: true
}

// Example: Tasks linked to Projects (N:1)
{
  table: 'Tasks',
  field: 'Project',
  type: 'multipleRecordLinks',
  linked_table: 'Projects',
  relationship: 'N:1',
  allow_multiple: false
}

// Lookup Field: Pull data from linked record
{
  field: 'Project Manager',
  type: 'lookup',
  linked_field: 'Project', // First follow this link
  lookup_field: 'Manager' // Then get this field from Projects table
}

// Rollup Field: Aggregate data from linked records
{
  field: 'Total Task Hours',
  type: 'rollup',
  linked_field: 'Tasks', // From Team Members table
  rollup_field: 'Estimated Hours',
  aggregation: 'SUM'
}
```

**View System:**
- **Grid View:** Spreadsheet interface, column resizing, frozen columns
- **Form View:** Public/private forms for data entry
- **Kanban View:** Group by single-select field, drag-and-drop
- **Calendar View:** Group by date field, multiple calendars
- **Gallery View:** Image-centric cards
- **Timeline View:** Gantt-style project timeline (2026 feature)

**2026 Trends:**
- **Airtable AI:** Auto-generate fields, formulas, relationships from natural language
- **Synced Tables:** Two-way sync between bases (shared objects across workspaces)
- **Advanced Permissions:** Row-level, field-level permissions

---

#### 3. Salesforce (Enterprise CRM Giant)

**Focus:** Enterprise CRM, Sales, Service, Marketing Cloud
**Architecture:** Object-oriented (sObject model)
**Complexity:** High (Apex code, Lightning components, complex permissions)
**Best Use Case:** Large enterprise CRM, custom business apps

**Core Architecture:**
```
Organization (Salesforce Instance)
  └── Application (e.g., "Sales Cloud")
       └── Objects (Standard + Custom)
            ├── Account (Standard Object)
            │    ├── Fields (Name, Industry, AnnualRevenue, Type)
            │    ├── Relationships
            │    │    ├── Lookup to Parent Account (Account Hierarchy)
            │    │    ├── Master-Detail to Owner (User)
            │    │    └── Junction via AccountContactRelation (N:N with Contact)
            │    ├── Validation Rules (e.g., "Phone must be 10 digits")
            │    ├── Workflow Rules (e.g., "Email sales manager when Revenue > $1M")
            │    ├── Page Layouts (different forms for Sales vs Support users)
            │    ├── Record Types (different processes for Enterprise vs SMB accounts)
            │    ├── Views
            │    │    ├── Account Record Page (Lightning Page with components)
            │    │    ├── Related Lists (Contacts, Opportunities, Cases)
            │    │    ├── List Views (My Accounts, New This Week, etc.)
            │    │    └── Kanban View (by Industry)
            │    └── Data (account records with permissions/sharing rules)
            ├── Contact (Standard Object)
            ├── Opportunity (Standard Object)
            ├── Case (Standard Object)
            └── Custom Objects (e.g., Invoice__c, Project__c)
```

**Object Model:**
- **Standard Objects:** Account, Contact, Lead, Opportunity, Case, etc. (pre-built)
- **Custom Objects:** Suffix with `__c` (e.g., `Invoice__c`)
- **sObject:** Base class for all objects (queryable via SOQL)
- **Schema Builder:** Visual tool to design objects and relationships

**Relationship System:**
```apex
// Example: Opportunity has Lookup to Account (N:1)
Account__c = {
  type: 'lookup',
  referenceTo: 'Account',
  relationshipName: 'AccountOpportunities',
  cascadeDelete: false // Account deletion doesn't delete Opportunities
}

// Example: Contact has Master-Detail to Account (N:1 with inheritance)
AccountId = {
  type: 'masterDetail',
  referenceTo: 'Account',
  relationshipName: 'Contacts',
  cascadeDelete: true, // Deleting Account deletes all Contacts
  reparentable: false, // Contact cannot be moved to another Account
  shareWithParent: true // Contact inherits Account's sharing rules
}

// Example: Opportunity ↔ Contact (N:N via Junction Object)
OpportunityContactRole (Junction Object) {
  OpportunityId: { type: 'masterDetail', referenceTo: 'Opportunity' },
  ContactId: { type: 'masterDetail', referenceTo: 'Contact' },
  Role: { type: 'picklist', values: ['Decision Maker', 'Influencer', 'User'] },
  IsPrimary: { type: 'checkbox' }
}
```

**Key Relationship Differences:**
- **Lookup:** Loosely coupled, no sharing inheritance, allows orphans
- **Master-Detail:** Tightly coupled, inherits security/sharing, cascade delete, rollup summaries

**View System:**
- **Lightning Pages:** Drag-and-drop components (Related Lists, Charts, Custom LWC)
- **List Views:** Filtered, sorted tables (public, private, shared)
- **Kanban View:** Group by picklist field (e.g., Opportunity Stage)
- **Related Lists:** Embedded in record pages (e.g., Account → Contacts)
- **Dashboards:** Real-time charts, reports, filters

**2026 Trends:**
- **Einstein AI:** Auto-populate fields, predict next best action
- **Hyperforce:** Multi-cloud architecture (AWS, Azure, GCP)
- **Flow Orchestrator:** Visual workflow builder with branching, approvals

---

#### 4. HubSpot (SMB CRM/Marketing Platform)

**Focus:** SMB CRM, Marketing Hub, Sales Hub, Service Hub
**Architecture:** Object-based (Standard + Custom Objects)
**Complexity:** Medium (user-friendly UI, some code for advanced features)
**Best Use Case:** SMB sales/marketing teams, inbound marketing

**Core Architecture:**
```
Account (HubSpot Instance)
  └── Hub (e.g., "Sales Hub")
       └── Objects
            ├── Contact (Standard Object)
            │    ├── Properties (Email, Phone, Lifecycle Stage, Lead Score)
            │    ├── Associations
            │    │    ├── Associated Companies (N:1, labeled "Works at")
            │    │    ├── Associated Deals (N:N, labeled "Involved in")
            │    │    └── Associated Tickets (N:N, labeled "Submitted by")
            │    ├── Workflows (e.g., "Send email when Lifecycle Stage = MQL")
            │    ├── Views
            │    │    ├── Record View (tabbed interface with timeline)
            │    │    ├── Table View (filterable contact list)
            │    │    └── Board View (Kanban by Lifecycle Stage)
            │    └── Data (contact records)
            ├── Company (Standard Object)
            ├── Deal (Standard Object)
            ├── Ticket (Standard Object)
            └── Custom Objects (e.g., Invoice, Project)
                 ├── Properties (custom fields)
                 ├── Associations (define relationships to other objects)
                 ├── Pipelines (multi-stage workflows like Deal pipelines)
                 └── Views (Table, Board, Record)
```

**Object Model:**
- **Standard Objects:** Contact, Company, Deal, Ticket, Product, Quote, etc.
- **Custom Objects:** User-defined (e.g., Courses, Events, Subscriptions)
- **Properties:** Fields within objects (Text, Number, Date, Dropdown, Multi-select)
- **Property Groups:** Organize properties (like fieldsets)

**Relationship System (Associations):**
```javascript
// Example: Contact → Company (N:1, labeled association)
{
  fromObject: 'Contact',
  toObject: 'Company',
  associationType: 'CONTACT_TO_COMPANY',
  label: 'Works at', // Custom label
  inverseLabel: 'Employees', // Label from Company side
  cardinality: 'N:1'
}

// Example: Deal ↔ Contact (N:N, labeled association)
{
  fromObject: 'Deal',
  toObject: 'Contact',
  associationType: 'DEAL_TO_CONTACT',
  label: 'Involved contacts',
  inverseLabel: 'Associated deals',
  cardinality: 'N:N',
  primaryAssociation: true // One contact marked as "Primary Contact"
}

// Custom Object Association: Invoice → Deal (N:1)
{
  fromObject: 'p123456_invoice', // Custom object with portal ID prefix
  toObject: 'Deal',
  associationType: 'INVOICE_TO_DEAL',
  label: 'Related deal',
  inverseLabel: 'Invoices',
  cardinality: 'N:1'
}
```

**Association Labels (2024-2026 Feature):**
- Each association has **custom labels** (e.g., "Works at", "Manager of")
- **Bi-directional labels** (Contact → Company: "Works at", Company → Contact: "Employees")
- **Multiple associations** between same object types (e.g., Contact → Contact: "Manager of", "Colleague of")

**View System:**
- **Record View:** Tabbed UI (About, Activity Timeline, Associations, Custom tabs)
- **Table View:** Filterable, sortable lists with saved views
- **Board View:** Kanban by pipeline stage or custom property
- **Reports:** Custom charts, funnels, attribution reports
- **Dashboards:** Collection of reports with filters

**2026 Trends:**
- **AI Content Assistant:** Auto-generate emails, blog posts from CRM data
- **Custom Objects API v4:** Full CRUD + associations via API
- **Advanced Permissions:** Object-level, record-level, field-level permissions

---

#### 5. Microsoft Dataverse (Power Platform Foundation)

**Focus:** Low-code platform for business apps (Power Apps, Power Automate)
**Architecture:** Table-based (formerly Common Data Service)
**Complexity:** Medium (visual tools, some Power Fx formulas)
**Best Use Case:** Internal business apps, process automation

**Core Architecture:**
```
Environment
  └── Solution (e.g., "Employee Onboarding App")
       └── Tables
            ├── Employee Table
            │    ├── Columns (Name, Email, Department, Hire Date)
            │    ├── Relationships
            │    │    ├── Lookup to Department Table (N:1)
            │    │    ├── 1:N to Onboarding Tasks (parent-child)
            │    │    └── N:N to Training Courses (via relationship table)
            │    ├── Business Rules (e.g., "Email required if Status = Active")
            │    ├── Forms
            │    │    ├── Main Form (for managers)
            │    │    ├── Quick Create Form (for HR)
            │    │    └── Mobile Form (simplified)
            │    ├── Views
            │    │    ├── Active Employees (filtered view)
            │    │    ├── New Hires This Month
            │    │    └── Associated Onboarding Tasks (related view)
            │    ├── Charts (e.g., Employees by Department pie chart)
            │    └── Data (employee records with security roles)
            ├── Department Table
            ├── Onboarding Tasks Table
            └── Training Courses Table
```

**Object Model:**
- **Standard Tables:** Account, Contact, User, Team (pre-built)
- **Custom Tables:** User-defined with prefix (e.g., `cr123_employee`)
- **Virtual Tables:** Read-only data from external sources (SharePoint, SQL Server)
- **Elastic Tables:** High-volume, high-speed data (IoT, logs) - 2025 feature

**Relationship System:**
```csharp
// Example: Employee → Department (N:1 Lookup)
{
  schemaName: 'cr123_employee_department',
  type: 'Lookup',
  referencingTable: 'cr123_employee',
  referencingColumn: 'cr123_departmentid',
  referencedTable: 'cr123_department',
  cascadeConfiguration: {
    assign: 'NoCascade',
    delete: 'RemoveLink', // Set to null when department deleted
    merge: 'Cascade',
    reparent: 'NoCascade'
  }
}

// Example: Employee → Onboarding Tasks (1:N with cascade)
{
  schemaName: 'cr123_employee_tasks',
  type: 'OneToMany',
  referencedTable: 'cr123_employee',
  referencingTable: 'cr123_onboardingtask',
  referencingColumn: 'cr123_employeeid',
  cascadeConfiguration: {
    delete: 'Cascade', // Delete tasks when employee deleted
    assign: 'Cascade', // Reassign tasks when employee reassigned
    share: 'Cascade',
    unshare: 'Cascade'
  }
}

// Example: Employee ↔ Training Courses (N:N)
{
  schemaName: 'cr123_employee_training',
  type: 'ManyToMany',
  entity1: 'cr123_employee',
  entity2: 'cr123_trainingcourse',
  intersectTable: 'cr123_employee_training', // Auto-generated junction table
  entity1NavigationProperty: 'cr123_employee_training_courses',
  entity2NavigationProperty: 'cr123_trainingcourse_employees'
}
```

**Cascade Behaviors:**
- **Cascade:** Apply action to related records (delete, assign, share)
- **Active:** Apply action only if related record is active
- **User Owned:** Apply action based on ownership
- **RemoveLink:** Set to null (for Lookups)
- **Restrict:** Prevent action if related records exist

**View System:**
- **Model-Driven Apps:** Auto-generated UI from table metadata
- **Canvas Apps:** Fully custom UI with Power Fx formulas
- **Forms:** Multiple forms per table (Main, Quick Create, Mobile, Card)
- **Views:** Saved queries (Public, Personal, System)
- **Dashboards:** Charts, lists, Power BI reports

**2026 Trends:**
- **Copilot Studio:** AI-powered app generation from natural language
- **Power Fx:** Excel-like formula language for logic (expanding to all Power Platform)
- **Dataverse for Teams:** Lightweight version integrated into Microsoft Teams

---

## Common Patterns Across All Platforms

### 1. Universal Hierarchy

**All platforms follow this structure:**

```
┌─────────────────────────────────────────────────┐
│ WORKSPACE / ORGANIZATION                        │
│ (Top-level container for all apps/data)         │
└───────────────────┬─────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │   APPLICATION       │
         │ (Collection of      │
         │  related objects)   │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         │   OBJECT / TABLE    │
         │ (Primary building   │
         │  block: Contact,    │
         │  Incident, Task)    │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┬──────────────┐
    │               │               │              │
┌───▼────┐   ┌──────▼──────┐  ┌────▼─────┐  ┌────▼────┐
│ FIELDS │   │RELATIONSHIPS│  │  VIEWS   │  │  DATA   │
│        │   │             │  │          │  │         │
│ Name   │   │ Contact→    │  │ Form     │  │ Record1 │
│ Email  │   │ Company     │  │ Table    │  │ Record2 │
│ Phone  │   │ (N:1 Lookup)│  │ Kanban   │  │ Record3 │
│ Status │   │             │  │ Calendar │  │ ...     │
└────────┘   └─────────────┘  └──────────┘  └─────────┘
```

**Platform-Specific Terminology:**

| Level | ServiceNow | Airtable | Salesforce | HubSpot | Dataverse |
|-------|-----------|----------|------------|---------|-----------|
| **Workspace** | Instance | Workspace | Organization | Account | Environment |
| **Application** | Application | Base | App | Hub | Solution |
| **Object** | Table | Table | Object (sObject) | Object | Table |
| **Fields** | Fields | Fields | Fields | Properties | Columns |
| **Relationships** | Reference | Linked Records | Lookup/Master-Detail | Associations | Lookup/1:N/N:N |
| **Views** | Forms/Lists | Grid/Form/Kanban | Lightning Pages | Record/Table/Board | Forms/Views |

### 2. Relationship Types (Universal Patterns)

All platforms support these core relationship types:

#### A. One-to-Many (1:N) / Lookup / Reference

**Concept:** One parent record relates to many child records
**Example:** One Company → Many Contacts
**Direction:** Child stores parent ID

```
COMPANY TABLE               CONTACT TABLE
┌─────────────┐            ┌──────────────────┐
│ id: 1       │◄───────────┤ company_id: 1    │  (Alice works for Acme Corp)
│ name: Acme  │            │ name: Alice      │
└─────────────┘            └──────────────────┘
                           ┌──────────────────┐
                   ────────┤ company_id: 1    │  (Bob works for Acme Corp)
                           │ name: Bob        │
                           └──────────────────┘
```

**Implementation Comparison:**

| Platform | Terminology | Delete Behavior | Allows NULL |
|----------|------------|-----------------|-------------|
| ServiceNow | Reference | Set NULL / Restrict | Yes |
| Airtable | Linked Records (single) | Remove Link | Yes |
| Salesforce | Lookup | Set NULL / Restrict | Yes |
| HubSpot | Association (N:1) | Remove Link | Yes |
| Dataverse | Lookup | RemoveLink / Restrict | Yes |

#### B. Master-Detail / Dependent / Cascade

**Concept:** One parent owns many children (tight coupling)
**Example:** One Problem → Many Child Incidents
**Behavior:** Deleting parent deletes all children

```
PROBLEM TABLE              INCIDENT TABLE
┌──────────────┐          ┌───────────────────────┐
│ id: P001     │◄─────────┤ parent_problem: P001  │  (Child incident)
│ title: DB    │          │ id: INC001            │  Delete P001 → Delete INC001
│ Outage       │          └───────────────────────┘
└──────────────┘          ┌───────────────────────┐
                  ────────┤ parent_problem: P001  │  (Child incident)
                          │ id: INC002            │  Delete P001 → Delete INC002
                          └───────────────────────┘
```

**Implementation Comparison:**

| Platform | Terminology | Cascade Delete | Shares Permissions | Rollup Summaries |
|----------|------------|----------------|-------------------|------------------|
| ServiceNow | Dependent Reference | Yes | No | No |
| Airtable | N/A (no strict master-detail) | No | No | Rollup Fields |
| Salesforce | Master-Detail | Yes | Yes (inherits) | Yes |
| HubSpot | N/A (all are Associations) | No | No | No |
| Dataverse | 1:N with Cascade Delete | Yes (configurable) | Yes (configurable) | Yes (calculated fields) |

#### C. Many-to-Many (N:N) / Junction

**Concept:** Records from two tables can relate to multiple records in the other
**Example:** Students ↔ Courses (student enrolls in multiple courses, course has multiple students)
**Implementation:** Junction table stores the relationships

```
STUDENT TABLE           ENROLLMENT TABLE            COURSE TABLE
┌──────────┐           ┌────────────────┐          ┌───────────┐
│ id: S1   │◄──────────┤ student_id: S1 │          │ id: C1    │
│ name: Amy│           │ course_id: C1  │──────────►│ Math 101  │
└──────────┘           │ grade: A       │          └───────────┘
                       └────────────────┘
                       ┌────────────────┐          ┌───────────┐
                       │ student_id: S1 │──────────►│ id: C2    │
                       │ course_id: C2  │          │ Physics   │
                       │ grade: B+      │          └───────────┘
                       └────────────────┘

┌──────────┐           ┌────────────────┐
│ id: S2   │◄──────────┤ student_id: S2 │
│ name: Ben│           │ course_id: C1  │──────────►(Math 101)
└──────────┘           │ grade: A-      │
                       └────────────────┘
```

**Implementation Comparison:**

| Platform | Junction Table | Additional Fields | Auto-created |
|----------|----------------|-------------------|--------------|
| ServiceNow | Manual (M2M table) | Yes | No (user creates) |
| Airtable | Auto (hidden) | No (link only) | Yes (automatic) |
| Salesforce | Auto (Junction Object) | Yes (add fields to junction) | Yes (when N:N created) |
| HubSpot | Auto (Associations) | No (2026: labels only) | Yes (automatic) |
| Dataverse | Auto (Intersect Table) | Yes (add columns) | Yes (automatic) |

### 3. View Types (Universal Patterns)

All platforms provide similar view types:

#### View Comparison Matrix

| View Type | Purpose | Use Case | ServiceNow | Airtable | Salesforce | HubSpot | Dataverse |
|-----------|---------|----------|-----------|----------|------------|---------|-----------|
| **Form** | CRUD operations | Create/edit single record | ✅ Forms | ✅ Form View | ✅ Lightning Page | ✅ Record View | ✅ Forms |
| **Table/List** | Browse records | View all contacts | ✅ List View | ✅ Grid View | ✅ List View | ✅ Table View | ✅ View |
| **Kanban** | Visual pipeline | Sales stage, task status | ✅ (custom) | ✅ Kanban View | ✅ Kanban View | ✅ Board View | ✅ (Power Apps) |
| **Calendar** | Time-based data | Events, deadlines | ✅ Calendar | ✅ Calendar View | ✅ Calendar View | ✅ (limited) | ✅ (Power Apps) |
| **Gallery** | Image-heavy | Product catalog | ❌ | ✅ Gallery View | ✅ (custom) | ❌ | ✅ (Power Apps) |
| **Related** | Show relationships | Company → Contacts | ✅ Related Lists | ✅ Linked Records | ✅ Related Lists | ✅ Associations | ✅ Subgrids |
| **Dashboard** | Analytics | KPIs, charts | ✅ Performance Analytics | ✅ Dashboard | ✅ Dashboard | ✅ Dashboard | ✅ Dashboard |

### 4. Field Types (Universal Core Set)

All platforms support these core field types:

| Category | Field Types | ServiceNow | Airtable | Salesforce | HubSpot | Dataverse |
|----------|-------------|-----------|----------|------------|---------|-----------|
| **Text** | Short text, Long text, Rich text | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Number** | Integer, Decimal, Currency, Percentage | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Date/Time** | Date, DateTime, Time | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Boolean** | Checkbox, True/False | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Choice** | Dropdown, Multi-select, Radio | ✅ Choice | ✅ Single/Multi Select | ✅ Picklist | ✅ Dropdown | ✅ Choice |
| **Lookup** | Reference to another object | ✅ Reference | ✅ Linked Records | ✅ Lookup | ✅ Association | ✅ Lookup |
| **User** | Reference to user/team | ✅ Reference (User) | ✅ Collaborator | ✅ Lookup (User) | ✅ Owner | ✅ Owner |
| **Email** | Email with validation | ✅ Email | ✅ Email | ✅ Email | ✅ Email | ✅ Email |
| **Phone** | Phone with formatting | ✅ Phone Number | ✅ Phone | ✅ Phone | ✅ Phone | ✅ Phone |
| **URL** | URL with validation | ✅ URL | ✅ URL | ✅ URL | ✅ URL | ✅ URL |
| **Attachment** | File upload | ✅ Attachment | ✅ Attachment | ✅ Files | ✅ File | ✅ File/Image |
| **Calculated** | Formula, Rollup | ✅ Calculated | ✅ Formula, Rollup | ✅ Formula | ✅ Calculated | ✅ Calculated |
| **Auto** | Auto-number, Created Date, Modified Date | ✅ | ✅ | ✅ | ✅ | ✅ |

### 5. Common Application Patterns

All platforms enable building these app types with similar structures:

#### Example: CRM Application

```
CRM Application
├── Lead Object
│   ├── Fields: Name, Email, Company, Source, Status
│   ├── Relationships: Convert to Contact/Opportunity
│   └── Views: Lead Form, Lead List (by Status), New Leads (Kanban)
├── Contact Object
│   ├── Fields: Name, Email, Phone, Title, Department
│   ├── Relationships: N:1 to Company, N:N to Opportunities
│   └── Views: Contact Form, All Contacts (Table), Contacts by Company (Related)
├── Company Object
│   ├── Fields: Name, Industry, Revenue, Type
│   ├── Relationships: 1:N to Contacts, 1:N to Opportunities
│   └── Views: Company Form, All Companies (Table), Pipeline by Company (Report)
└── Opportunity Object
    ├── Fields: Title, Amount, Stage, Close Date, Probability
    ├── Relationships: N:1 to Company, N:1 to Contact (Primary), N:N to Contacts (Involved)
    └── Views: Opportunity Form, Sales Pipeline (Kanban by Stage), Forecast Report
```

#### Example: ITSM Application

```
ITSM Application
├── Incident Object
│   ├── Fields: Number, Description, Priority, State, Assigned To, Affected User
│   ├── Relationships: N:1 to User (Assigned), N:1 to Configuration Item, N:1 to Problem
│   └── Views: Incident Form, My Incidents (List), Open Incidents (Kanban by Priority)
├── Problem Object
│   ├── Fields: Number, Root Cause, Workaround, State
│   ├── Relationships: 1:N to Incidents (Dependent), N:1 to Configuration Item
│   └── Views: Problem Form, Active Problems (List), Related Incidents (Related List)
├── Change Request Object
│   ├── Fields: Number, Description, Risk, Impact, State, Scheduled Start
│   ├── Relationships: N:1 to Configuration Item, N:N to Incidents (Resolved By)
│   └── Views: Change Form, Change Calendar, Approval Board (Kanban)
└── Configuration Item Object
    ├── Fields: Name, Type, Serial Number, Location, Owner
    ├── Relationships: 1:N to Incidents, 1:N to Problems, 1:N to Changes
    └── Views: CI Form, Asset List (Table), CI Map (Relationship Diagram)
```

---

## Recommended Architecture for Our Platform

### Core Principles

Based on research, our platform should follow these principles:

1. **Object-First, Not Form-First**
   - Users create Objects (tables/entities), not forms
   - Forms are just one view type for an Object
   - Objects are reusable across applications

2. **Relationships as First-Class Citizens**
   - Relationships defined between Objects (not hardcoded in views)
   - Support Lookup (N:1), One-to-Many (1:N), Many-to-Many (N:N)
   - Cascade behaviors configurable (delete, update)

3. **Multiple Views Per Object**
   - Each Object can have multiple views (Form, Table, Kanban, Calendar)
   - Views are auto-generated from Object schema but customizable
   - Users can create unlimited custom views with filters/sorting

4. **Application = Collection of Related Objects**
   - Users build Applications by selecting/creating Objects
   - Define relationships between Objects
   - Configure workflows/automations across Objects

### Proposed Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ WORKSPACE                                               │
│ (User's top-level container)                            │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │   APPLICATION       │
          │ (CRM, ITSM, etc.)   │
          ├─────────────────────┤
          │ - Name              │
          │ - Description       │
          │ - Objects: []       │  ← Array of Object IDs
          │ - Relationships: [] │  ← Relationships between objects
          │ - Navigation: []    │  ← Menu structure
          └──────────┬──────────┘
                     │
          ┌──────────┴──────────┐
          │   OBJECT            │
          │ (Contact, Incident) │
          ├─────────────────────┤
          │ - Name              │
          │ - Plural Name       │
          │ - Icon              │
          │ - Fields: []        │  ← Field definitions
          │ - Views: {          │
          │     form: [],       │  ← Multiple form layouts
          │     table: [],      │  ← Multiple table views
          │     kanban: [],     │  ← Multiple kanban views
          │     calendar: []    │  ← Multiple calendar views
          │   }                 │
          │ - Permissions: {}   │  ← Who can CRUD
          └──────────┬──────────┘
                     │
    ┌────────────────┼────────────────┬─────────────────┐
    │                │                │                 │
┌───▼────┐   ┌───────▼────────┐  ┌───▼──────┐   ┌─────▼──────┐
│ FIELD  │   │ RELATIONSHIP   │  │   VIEW   │   │    DATA    │
├────────┤   ├────────────────┤  ├──────────┤   ├────────────┤
│ name   │   │ type: lookup   │  │ type:    │   │ record_1   │
│ type   │   │ from: Contact  │  │  form    │   │ record_2   │
│ req'd  │   │ to: Company    │  │ fields   │   │ record_3   │
│ valid. │   │ label: Works at│  │ layout   │   │ ...        │
└────────┘   └────────────────┘  └──────────┘   └────────────┘
```

### Data Model Schema (TypeScript)

```typescript
// ==================== OBJECT DEFINITION ====================

interface Object {
  id: string; // Unique object ID (e.g., "obj_contact_abc123")
  name: string; // Singular name (e.g., "Contact")
  pluralName: string; // Plural name (e.g., "Contacts")
  description: string;
  icon: string; // Icon identifier
  isCustom: boolean; // true for user-created, false for standard objects

  // Fields
  fields: Field[];

  // Relationships to other objects
  relationships: Relationship[];

  // Views (multiple per type)
  views: {
    forms: FormView[];
    tables: TableView[];
    kanbans: KanbanView[];
    calendars: CalendarView[];
  };

  // Permissions
  permissions: {
    create: string[]; // User roles that can create records
    read: string[];
    update: string[];
    delete: string[];
  };

  // Metadata
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

// ==================== FIELD DEFINITION ====================

interface Field {
  id: string; // Unique field ID (e.g., "fld_email_xyz789")
  name: string; // Field name (e.g., "Email Address")
  apiName: string; // API-safe name (e.g., "email_address")
  type: FieldType;

  // Validation
  required: boolean;
  unique: boolean;
  validation?: ValidationRule[];

  // Type-specific config
  config: FieldConfig;

  // UI
  helpText?: string;
  placeholder?: string;
  defaultValue?: any;

  // Permissions
  readOnly: boolean;
  visibleToRoles: string[];
  editableByRoles: string[];
}

type FieldType =
  | 'text'
  | 'longtext'
  | 'richtext'
  | 'email'
  | 'phone'
  | 'url'
  | 'number'
  | 'currency'
  | 'percentage'
  | 'date'
  | 'datetime'
  | 'time'
  | 'checkbox'
  | 'dropdown'
  | 'multiselect'
  | 'radio'
  | 'lookup' // Reference to another object (N:1)
  | 'user'
  | 'file'
  | 'image'
  | 'formula'
  | 'rollup'
  | 'autonumber';

interface FieldConfig {
  // Dropdown/Radio/Multiselect
  options?: { label: string; value: string; color?: string }[];

  // Lookup
  lookupObject?: string; // Object ID to look up
  lookupDisplayField?: string; // Field to display from lookup

  // Number/Currency
  min?: number;
  max?: number;
  decimals?: number;
  currencySymbol?: string; // For currency fields

  // Text
  maxLength?: number;

  // Formula
  formula?: string; // Expression like "amount * 0.1"

  // Rollup
  rollupObject?: string; // Related object to aggregate
  rollupField?: string; // Field to aggregate
  rollupFunction?: 'SUM' | 'AVG' | 'COUNT' | 'MIN' | 'MAX';

  // Autonumber
  prefix?: string;
  startingNumber?: number;
}

// ==================== RELATIONSHIP DEFINITION ====================

interface Relationship {
  id: string;
  type: RelationshipType;

  // Objects involved
  fromObject: string; // Object ID
  toObject: string; // Object ID

  // Labels
  label: string; // Label from source (e.g., "Works at")
  inverseLabel: string; // Label from target (e.g., "Employees")

  // Configuration
  required: boolean; // Is relationship required?
  cascadeDelete: boolean; // Delete children when parent deleted?

  // For Many-to-Many
  junctionTable?: string; // Auto-generated junction table name
}

type RelationshipType =
  | 'lookup' // N:1 (many records of fromObject → one record of toObject)
  | 'oneToMany' // 1:N (one parent → many children, same as inverse of lookup)
  | 'manyToMany'; // N:N (many-to-many via junction table)

// ==================== VIEW DEFINITIONS ====================

interface FormView {
  id: string;
  name: string; // e.g., "Contact Form", "Quick Create Contact"
  isDefault: boolean;

  // Layout
  sections: FormSection[];

  // Behavior
  showRelatedLists: boolean; // Show related records at bottom
  relatedLists?: RelatedListConfig[];
}

interface FormSection {
  title: string;
  columns: number; // 1, 2, or 3 columns
  fields: string[]; // Field IDs in this section
}

interface RelatedListConfig {
  relatedObject: string; // Object ID
  relationshipId: string; // Relationship ID
  label: string; // e.g., "Related Opportunities"
  fields: string[]; // Fields to display in related list
}

interface TableView {
  id: string;
  name: string; // e.g., "All Contacts", "My Active Contacts"
  isDefault: boolean;

  // Columns
  columns: TableColumn[];

  // Filtering
  filters?: FilterRule[];

  // Sorting
  sortBy?: { field: string; direction: 'asc' | 'desc' }[];

  // Pagination
  pageSize: number;

  // Actions
  enableInlineEdit: boolean;
  bulkActions: string[]; // ['delete', 'export', 'assign']
}

interface TableColumn {
  fieldId: string;
  width?: number;
  visible: boolean;
  locked: boolean; // Frozen column
}

interface KanbanView {
  id: string;
  name: string; // e.g., "Sales Pipeline", "Incidents by Status"
  isDefault: boolean;

  // Grouping
  groupByField: string; // Field ID (must be dropdown/radio)

  // Columns
  columns: KanbanColumn[];

  // Card config
  cardTitleField: string; // Field to show as card title
  cardFields: string[]; // Additional fields on card

  // Filtering
  filters?: FilterRule[];
}

interface KanbanColumn {
  value: string; // Option value from groupByField
  label: string;
  color: string;
  limit?: number; // WIP limit (Work In Progress)
}

interface CalendarView {
  id: string;
  name: string;
  isDefault: boolean;

  // Date config
  dateField: string; // Field ID (must be date/datetime)
  endDateField?: string; // For multi-day events

  // Display
  titleField: string; // Field to show as event title
  colorField?: string; // Field to color-code events (e.g., status)

  // Filtering
  filters?: FilterRule[];
}

interface FilterRule {
  field: string; // Field ID
  operator: 'equals' | 'notEquals' | 'contains' | 'greaterThan' | 'lessThan' | 'isEmpty' | 'isNotEmpty';
  value: any;
}

// ==================== APPLICATION DEFINITION ====================

interface Application {
  id: string;
  name: string; // e.g., "CRM", "ITSM", "Inventory"
  description: string;
  icon: string;

  // Objects in this application
  objects: string[]; // Object IDs

  // Navigation menu
  navigation: NavItem[];

  // Permissions
  permissions: {
    viewApp: string[]; // Roles that can access app
    editApp: string[]; // Roles that can modify app structure
  };

  // Metadata
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  publishedAt?: string;
}

interface NavItem {
  label: string;
  type: 'object' | 'view' | 'report' | 'dashboard' | 'separator';
  objectId?: string; // For type: 'object'
  viewId?: string; // For type: 'view'
  icon?: string;
  children?: NavItem[]; // For nested menus
}
```

### Database Schema (Supabase PostgreSQL)

```sql
-- ==================== OBJECTS TABLE ====================
CREATE TABLE objects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  plural_name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  is_custom BOOLEAN DEFAULT true,

  -- JSON columns for complex data
  fields JSONB NOT NULL DEFAULT '[]', -- Array of Field objects
  relationships JSONB NOT NULL DEFAULT '[]', -- Array of Relationship objects
  views JSONB NOT NULL DEFAULT '{"forms": [], "tables": [], "kanbans": [], "calendars": []}',
  permissions JSONB NOT NULL DEFAULT '{"create": [], "read": [], "update": [], "delete": []}',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),

  -- Indexes
  UNIQUE(name, created_by) -- User can't have duplicate object names
);

CREATE INDEX idx_objects_created_by ON objects(created_by);
CREATE INDEX idx_objects_is_custom ON objects(is_custom);

-- ==================== APPLICATIONS TABLE ====================
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,

  -- Objects in this app
  objects JSONB NOT NULL DEFAULT '[]', -- Array of object IDs

  -- Navigation
  navigation JSONB NOT NULL DEFAULT '[]', -- Array of NavItem objects

  -- Permissions
  permissions JSONB NOT NULL DEFAULT '{"viewApp": [], "editApp": []}',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),
  published_at TIMESTAMPTZ,

  UNIQUE(name, created_by)
);

CREATE INDEX idx_applications_created_by ON applications(created_by);

-- ==================== RECORDS TABLE (Dynamic Data) ====================
-- This table stores actual data for all objects
CREATE TABLE records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,

  -- Dynamic data stored as JSONB
  data JSONB NOT NULL DEFAULT '{}',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES auth.users(id),
  updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_records_object_id ON records(object_id);
CREATE INDEX idx_records_created_by ON records(created_by);
CREATE INDEX idx_records_data ON records USING GIN(data); -- For fast JSONB queries

-- ==================== RELATIONSHIPS TABLE (Junction for N:N) ====================
-- Auto-generated junction tables for many-to-many relationships
CREATE TABLE relationship_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  relationship_id TEXT NOT NULL, -- From objects.relationships[].id
  from_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,
  to_record_id UUID NOT NULL REFERENCES records(id) ON DELETE CASCADE,

  -- Additional fields for N:N relationships (e.g., role, start_date)
  metadata JSONB DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(relationship_id, from_record_id, to_record_id)
);

CREATE INDEX idx_relationship_records_from ON relationship_records(from_record_id);
CREATE INDEX idx_relationship_records_to ON relationship_records(to_record_id);
CREATE INDEX idx_relationship_records_rel ON relationship_records(relationship_id);

-- ==================== FIELD TEMPLATES TABLE ====================
-- Reusable field configurations
CREATE TABLE field_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  field_config JSONB NOT NULL, -- Full Field object
  category TEXT, -- e.g., "Contact Info", "Financial", "Custom"
  usage_count INTEGER DEFAULT 0,
  is_global BOOLEAN DEFAULT false, -- Available to all users
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_field_templates_category ON field_templates(category);
CREATE INDEX idx_field_templates_global ON field_templates(is_global);

-- ==================== TRIGGERS ====================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER objects_updated_at BEFORE UPDATE ON objects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER applications_updated_at BEFORE UPDATE ON applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER records_updated_at BEFORE UPDATE ON records
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Example: How Data is Stored

**Objects Table:**
```json
{
  "id": "obj_contact_001",
  "name": "Contact",
  "plural_name": "Contacts",
  "fields": [
    {
      "id": "fld_name",
      "name": "Full Name",
      "apiName": "full_name",
      "type": "text",
      "required": true,
      "config": { "maxLength": 100 }
    },
    {
      "id": "fld_email",
      "name": "Email",
      "apiName": "email",
      "type": "email",
      "required": true,
      "unique": true,
      "config": {}
    },
    {
      "id": "fld_company",
      "name": "Company",
      "apiName": "company",
      "type": "lookup",
      "required": false,
      "config": {
        "lookupObject": "obj_company_001",
        "lookupDisplayField": "name"
      }
    }
  ],
  "relationships": [
    {
      "id": "rel_contact_company",
      "type": "lookup",
      "fromObject": "obj_contact_001",
      "toObject": "obj_company_001",
      "label": "Works at",
      "inverseLabel": "Employees",
      "required": false,
      "cascadeDelete": false
    }
  ],
  "views": {
    "forms": [
      {
        "id": "form_contact_main",
        "name": "Contact Form",
        "isDefault": true,
        "sections": [
          {
            "title": "Basic Information",
            "columns": 2,
            "fields": ["fld_name", "fld_email", "fld_company"]
          }
        ]
      }
    ],
    "tables": [
      {
        "id": "table_all_contacts",
        "name": "All Contacts",
        "isDefault": true,
        "columns": [
          { "fieldId": "fld_name", "visible": true },
          { "fieldId": "fld_email", "visible": true },
          { "fieldId": "fld_company", "visible": true }
        ],
        "pageSize": 25
      }
    ]
  }
}
```

**Records Table (actual contact data):**
```json
{
  "id": "rec_12345",
  "object_id": "obj_contact_001",
  "data": {
    "full_name": "Alice Johnson",
    "email": "alice@example.com",
    "company": "rec_company_67890" // Reference to company record
  },
  "created_at": "2026-01-15T10:30:00Z",
  "created_by": "user_abc"
}
```

---

## Concrete Example: Building a CRM

### Current Wrong Approach (Template-Centric)

```
User Flow (WRONG):
1. User clicks "Create New Project"
2. Selects "Form" template
3. Names it "Customer Form"
4. Adds fields: Name, Email, Company, Phone
5. System auto-generates Table view and Kanban view
6. User publishes

Problem:
- Can't create "Opportunity" form that relates to "Customer"
- Can't see "All opportunities for this customer"
- Can't create master-detail relationships
- Application is just a single form, not a real CRM
```

### Correct Approach (Object-Centric)

```
User Flow (CORRECT):
1. User clicks "Create New Application"
2. Names it "Sales CRM"
3. Chooses template: "CRM" (pre-configured objects) OR starts blank

4. CREATE OBJECTS:

   a) Create "Contact" Object
      - Fields: Full Name, Email, Phone, Title, LinkedIn
      - Icon: User icon
      - Save

   b) Create "Company" Object
      - Fields: Name, Industry, Revenue, Employee Count, Website
      - Icon: Building icon
      - Save

   c) Create "Opportunity" Object
      - Fields: Title, Amount, Stage, Close Date, Probability
      - Icon: Dollar icon
      - Save

5. DEFINE RELATIONSHIPS:

   a) Contact → Company (N:1 Lookup)
      - From: Contact
      - To: Company
      - Label: "Works at"
      - Inverse Label: "Employees"
      - Required: No
      - Cascade Delete: No (keep contacts when company deleted)

   b) Opportunity → Company (N:1 Lookup)
      - From: Opportunity
      - To: Company
      - Label: "Related to"
      - Inverse Label: "Opportunities"
      - Required: Yes
      - Cascade Delete: Yes (delete opps when company deleted)

   c) Opportunity → Contact (Primary) (N:1 Lookup)
      - From: Opportunity
      - To: Contact
      - Label: "Owner"
      - Inverse Label: "Owned Opportunities"
      - Required: Yes

   d) Opportunity ↔ Contact (Involved Contacts) (N:N)
      - From: Opportunity
      - To: Contact
      - Label: "Involved Contacts"
      - Inverse Label: "Opportunities I'm Involved In"
      - Junction Table: Auto-created
      - Additional Fields: Role (Decision Maker, Influencer, User)

6. CONFIGURE VIEWS FOR EACH OBJECT:

   a) Contact Object Views:
      - Form: "Contact Form" (fields: Name, Email, Phone, Company lookup)
      - Table: "All Contacts" (columns: Name, Email, Company, Phone)
      - Kanban: "Contacts by Company" (group by Company)
      - Related Lists:
         * Related Opportunities (shows opps where contact is owner)
         * Involved Opportunities (shows opps where contact is involved)

   b) Company Object Views:
      - Form: "Company Form" (fields: Name, Industry, Revenue, Website)
      - Table: "All Companies" (columns: Name, Industry, Revenue, # Employees)
      - Gallery: "Company Gallery" (card view with logo/website)
      - Related Lists:
         * Employees (all contacts at this company)
         * Opportunities (all opps for this company)

   c) Opportunity Object Views:
      - Form: "Opportunity Form" (fields: Title, Amount, Stage dropdown, Close Date, Company lookup, Owner lookup)
      - Table: "All Opportunities" (columns: Title, Company, Amount, Stage, Close Date)
      - Kanban: "Sales Pipeline" (group by Stage: Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
      - Calendar: "Close Dates" (show opps by close date)
      - Related Lists:
         * Involved Contacts (all contacts involved in this opp)

7. CONFIGURE NAVIGATION:
   - Home Dashboard
   - Contacts (opens All Contacts table)
   - Companies (opens All Companies table)
   - Opportunities (opens Sales Pipeline kanban)
   - Reports
     - Sales Forecast
     - Win Rate by Industry

8. PUBLISH APPLICATION
   - Application is now live
   - Users can navigate between objects
   - Relationships are clickable (Contact → view their Company → view all Opportunities for that Company)
```

### Visual Comparison

**Wrong Approach (Current):**
```
┌─────────────────────────────────┐
│  "Customer Form" Application    │
├─────────────────────────────────┤
│                                 │
│  Form View                      │
│  Table View (auto-generated)    │
│  Kanban View (auto-generated)   │
│                                 │
│  Records:                       │
│  - Alice (alice@acme.com)       │
│  - Bob (bob@widgets.com)        │
│                                 │
│  ❌ No relationships            │
│  ❌ Can't link to "Company"     │
│  ❌ Can't create "Opportunity"  │
└─────────────────────────────────┘
```

**Correct Approach (Proposed):**
```
┌───────────────────────────────────────────────────────────────┐
│  "Sales CRM" Application                                      │
├───────────────────────────────────────────────────────────────┤
│  Navigation:                                                  │
│  [Contacts] [Companies] [Opportunities] [Reports]             │
└───────────────────────────────────────────────────────────────┘
        │           │            │
        ▼           ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────────┐
│  CONTACT    │  │  COMPANY    │  │  OPPORTUNITY    │
├─────────────┤  ├─────────────┤  ├─────────────────┤
│ Fields:     │  │ Fields:     │  │ Fields:         │
│ - Name      │  │ - Name      │  │ - Title         │
│ - Email     │  │ - Industry  │  │ - Amount        │
│ - Company ──┼──┤ - Revenue   │  │ - Stage         │
│             │  │             │  │ - Company ──────┤
│             │  │             │  │ - Owner ────────┤
│             │  │             │  │                 │
│ Views:      │  │ Views:      │  │ Views:          │
│ - Form      │  │ - Form      │  │ - Form          │
│ - Table     │  │ - Table     │  │ - Kanban (Stage)│
│ - Kanban    │  │ - Gallery   │  │ - Calendar      │
│             │  │             │  │                 │
│ Related:    │  │ Related:    │  │ Related:        │
│ - Opps      │  │ - Employees │  │ - Contacts      │
│   Owned     │  │ - Opps      │  │   (N:N)         │
└─────────────┘  └─────────────┘  └─────────────────┘
```

### User Experience: Navigating Relationships

**Scenario:** User wants to see all opportunities for Acme Corp

**Wrong Approach (Current):**
```
1. Open "Customer Form" table view
2. Find "Acme Corp" row
3. ❌ No way to see related opportunities
4. User has to manually filter "Opportunity Form" table by company name
```

**Correct Approach (Proposed):**
```
1. Open "Companies" table view
2. Click on "Acme Corp" → Opens Company record page
3. Scroll to "Related Opportunities" section
4. See all opportunities:
   ┌──────────────────────────────────────────────────┐
   │ Related Opportunities (3)                        │
   ├──────────────────────────────────────────────────┤
   │ Title              Amount     Stage      Owner   │
   ├──────────────────────────────────────────────────┤
   │ Q1 Enterprise Deal $500,000   Proposal   Alice   │ ← Click to open
   │ Website Redesign   $50,000    Qualified  Bob     │
   │ Support Contract   $120,000   Negotiation Charlie│
   └──────────────────────────────────────────────────┘
5. Click on "Q1 Enterprise Deal" → Opens Opportunity record
6. See "Involved Contacts" (N:N relationship):
   ┌──────────────────────────────────────────────────┐
   │ Involved Contacts (4)                            │
   ├──────────────────────────────────────────────────┤
   │ Name          Role            Email              │
   ├──────────────────────────────────────────────────┤
   │ Alice (Owner) Decision Maker  alice@acme.com     │
   │ Dan           Influencer      dan@acme.com       │
   │ Eve           User            eve@acme.com       │
   │ Frank         User            frank@acme.com     │
   └──────────────────────────────────────────────────┘
```

---

## Technical Implementation Proposal

### Frontend Component Structure

```
src/
├── pages/
│   ├── ApplicationBuilder.tsx       // Main app builder UI
│   ├── ObjectDesigner.tsx           // Object field/relationship editor
│   ├── ViewConfigurator.tsx         // Configure forms/tables/kanbans
│   └── ApplicationRuntime.tsx       // Runtime app viewer
│
├── components/
│   ├── object/
│   │   ├── ObjectList.tsx           // List of objects in app
│   │   ├── ObjectEditor.tsx         // Edit object schema
│   │   ├── FieldEditor.tsx          // Add/edit fields
│   │   └── RelationshipEditor.tsx   // Define relationships
│   │
│   ├── view/
│   │   ├── FormViewEditor.tsx       // Design form layouts
│   │   ├── TableViewEditor.tsx      // Configure table columns
│   │   ├── KanbanViewEditor.tsx     // Configure kanban
│   │   └── CalendarViewEditor.tsx   // Configure calendar
│   │
│   ├── runtime/
│   │   ├── RecordPage.tsx           // Single record detail page
│   │   ├── ListView.tsx             // Table view of records
│   │   ├── KanbanView.tsx           // Kanban board
│   │   ├── CalendarView.tsx         // Calendar view
│   │   └── RelatedList.tsx          // Related records section
│   │
│   └── relationship/
│       ├── LookupField.tsx          // Lookup/reference field UI
│       ├── RelatedRecordsList.tsx   // Show related records
│       └── ManyToManyEditor.tsx     // Manage N:N relationships
│
├── stores/
│   ├── applicationStore.ts          // Application-level state
│   ├── objectStore.ts               // Object definitions
│   ├── recordStore.ts               // Record data (CRUD)
│   └── relationshipStore.ts         // Relationship data
│
├── services/
│   ├── objectService.ts             // CRUD for objects
│   ├── recordService.ts             // CRUD for records
│   ├── relationshipService.ts       // Manage relationships
│   └── viewService.ts               // Auto-generate views
│
└── types/
    ├── object.ts                    // Object, Field, Relationship types
    ├── application.ts               // Application, NavItem types
    ├── view.ts                      // FormView, TableView, etc.
    └── record.ts                    // Record, RecordData types
```

### Store Architecture (Zustand)

```typescript
// ==================== objectStore.ts ====================
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ObjectStore {
  // State
  objects: Object[];
  activeObjectId: string | null;

  // Actions
  createObject: (object: Omit<Object, 'id' | 'createdAt'>) => void;
  updateObject: (id: string, updates: Partial<Object>) => void;
  deleteObject: (id: string) => void;

  // Field actions
  addField: (objectId: string, field: Omit<Field, 'id'>) => void;
  updateField: (objectId: string, fieldId: string, updates: Partial<Field>) => void;
  deleteField: (objectId: string, fieldId: string) => void;

  // Relationship actions
  addRelationship: (objectId: string, relationship: Omit<Relationship, 'id'>) => void;
  updateRelationship: (objectId: string, relId: string, updates: Partial<Relationship>) => void;
  deleteRelationship: (objectId: string, relId: string) => void;

  // View actions
  addView: (objectId: string, viewType: 'forms' | 'tables' | 'kanbans' | 'calendars', view: any) => void;
  updateView: (objectId: string, viewType: string, viewId: string, updates: any) => void;
  deleteView: (objectId: string, viewType: string, viewId: string) => void;

  // Auto-generation
  autoGenerateViews: (objectId: string) => void; // Generate default views from schema
}

export const useObjectStore = create<ObjectStore>()(
  persist(
    (set, get) => ({
      objects: [],
      activeObjectId: null,

      createObject: (objectData) => {
        const newObject: Object = {
          ...objectData,
          id: `obj_${Date.now()}`,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          fields: objectData.fields || [],
          relationships: objectData.relationships || [],
          views: {
            forms: [],
            tables: [],
            kanbans: [],
            calendars: []
          }
        };

        set({ objects: [...get().objects, newObject] });

        // Auto-generate default views
        get().autoGenerateViews(newObject.id);
      },

      updateObject: (id, updates) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === id
              ? { ...obj, ...updates, updatedAt: new Date().toISOString() }
              : obj
          )
        });
      },

      deleteObject: (id) => {
        set({ objects: get().objects.filter(obj => obj.id !== id) });
      },

      addField: (objectId, fieldData) => {
        const newField: Field = {
          ...fieldData,
          id: `fld_${Date.now()}`,
        };

        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  fields: [...obj.fields, newField],
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });

        // Re-generate views to include new field
        get().autoGenerateViews(objectId);
      },

      updateField: (objectId, fieldId, updates) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  fields: obj.fields.map(f =>
                    f.id === fieldId ? { ...f, ...updates } : f
                  ),
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      deleteField: (objectId, fieldId) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  fields: obj.fields.filter(f => f.id !== fieldId),
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      addRelationship: (objectId, relData) => {
        const newRel: Relationship = {
          ...relData,
          id: `rel_${Date.now()}`,
        };

        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  relationships: [...obj.relationships, newRel],
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      updateRelationship: (objectId, relId, updates) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  relationships: obj.relationships.map(r =>
                    r.id === relId ? { ...r, ...updates } : r
                  ),
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      deleteRelationship: (objectId, relId) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  relationships: obj.relationships.filter(r => r.id !== relId),
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      addView: (objectId, viewType, view) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  views: {
                    ...obj.views,
                    [viewType]: [...obj.views[viewType], { ...view, id: `view_${Date.now()}` }]
                  },
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      updateView: (objectId, viewType, viewId, updates) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  views: {
                    ...obj.views,
                    [viewType]: obj.views[viewType].map(v =>
                      v.id === viewId ? { ...v, ...updates } : v
                    )
                  },
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      deleteView: (objectId, viewType, viewId) => {
        set({
          objects: get().objects.map(obj =>
            obj.id === objectId
              ? {
                  ...obj,
                  views: {
                    ...obj.views,
                    [viewType]: obj.views[viewType].filter(v => v.id !== viewId)
                  },
                  updatedAt: new Date().toISOString()
                }
              : obj
          )
        });
      },

      autoGenerateViews: (objectId) => {
        const object = get().objects.find(o => o.id === objectId);
        if (!object) return;

        // Generate default Form view
        if (object.views.forms.length === 0) {
          const defaultForm: FormView = {
            id: `form_${Date.now()}`,
            name: `${object.name} Form`,
            isDefault: true,
            sections: [
              {
                title: 'Information',
                columns: 2,
                fields: object.fields.map(f => f.id)
              }
            ],
            showRelatedLists: true,
            relatedLists: object.relationships
              .filter(r => r.type === 'oneToMany')
              .map(r => ({
                relatedObject: r.toObject,
                relationshipId: r.id,
                label: r.inverseLabel,
                fields: [] // Will be populated later
              }))
          };

          get().addView(objectId, 'forms', defaultForm);
        }

        // Generate default Table view
        if (object.views.tables.length === 0) {
          const defaultTable: TableView = {
            id: `table_${Date.now()}`,
            name: `All ${object.pluralName}`,
            isDefault: true,
            columns: object.fields
              .filter(f => ['text', 'email', 'phone', 'dropdown', 'lookup'].includes(f.type))
              .slice(0, 5) // First 5 fields
              .map(f => ({
                fieldId: f.id,
                visible: true,
                locked: false
              })),
            pageSize: 25,
            enableInlineEdit: true,
            bulkActions: ['delete', 'export']
          };

          get().addView(objectId, 'tables', defaultTable);
        }

        // Generate Kanban view if there's a dropdown/radio field
        const kanbanField = object.fields.find(f =>
          ['dropdown', 'radio', 'multiselect'].includes(f.type) && f.config.options
        );

        if (kanbanField && object.views.kanbans.length === 0) {
          const defaultKanban: KanbanView = {
            id: `kanban_${Date.now()}`,
            name: `${object.pluralName} by ${kanbanField.name}`,
            isDefault: true,
            groupByField: kanbanField.id,
            columns: kanbanField.config.options!.map(opt => ({
              value: opt.value,
              label: opt.label,
              color: opt.color || '#3b82f6'
            })),
            cardTitleField: object.fields[0]?.id || '', // First field as title
            cardFields: object.fields.slice(1, 4).map(f => f.id) // Next 3 fields
          };

          get().addView(objectId, 'kanbans', defaultKanban);
        }
      }
    }),
    {
      name: 'object-storage'
    }
  )
);

// ==================== recordStore.ts ====================
interface RecordStore {
  // State
  records: Record<string, any[]>; // Keyed by objectId: { obj_contact_001: [record1, record2] }

  // Actions
  getRecords: (objectId: string) => any[];
  getRecord: (objectId: string, recordId: string) => any | null;
  createRecord: (objectId: string, data: any) => void;
  updateRecord: (objectId: string, recordId: string, data: any) => void;
  deleteRecord: (objectId: string, recordId: string) => void;

  // Relationship queries
  getRelatedRecords: (objectId: string, recordId: string, relationshipId: string) => any[];
  linkRecords: (relationshipId: string, fromRecordId: string, toRecordId: string, metadata?: any) => void;
  unlinkRecords: (relationshipId: string, fromRecordId: string, toRecordId: string) => void;
}

export const useRecordStore = create<RecordStore>()(
  persist(
    (set, get) => ({
      records: {},

      getRecords: (objectId) => {
        return get().records[objectId] || [];
      },

      getRecord: (objectId, recordId) => {
        const records = get().records[objectId] || [];
        return records.find(r => r.id === recordId) || null;
      },

      createRecord: (objectId, data) => {
        const newRecord = {
          id: `rec_${Date.now()}`,
          ...data,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };

        set({
          records: {
            ...get().records,
            [objectId]: [...(get().records[objectId] || []), newRecord]
          }
        });
      },

      updateRecord: (objectId, recordId, data) => {
        set({
          records: {
            ...get().records,
            [objectId]: (get().records[objectId] || []).map(r =>
              r.id === recordId
                ? { ...r, ...data, updatedAt: new Date().toISOString() }
                : r
            )
          }
        });
      },

      deleteRecord: (objectId, recordId) => {
        set({
          records: {
            ...get().records,
            [objectId]: (get().records[objectId] || []).filter(r => r.id !== recordId)
          }
        });
      },

      getRelatedRecords: (objectId, recordId, relationshipId) => {
        // Implementation depends on relationship type
        // For N:1 Lookup: find records where field value = recordId
        // For 1:N: find records in toObject where lookup field = recordId
        // For N:N: query relationship_records table
        // TODO: Implement based on relationship type
        return [];
      },

      linkRecords: (relationshipId, fromRecordId, toRecordId, metadata = {}) => {
        // Store in separate relationship_records storage
        // TODO: Implement N:N junction table logic
      },

      unlinkRecords: (relationshipId, fromRecordId, toRecordId) => {
        // Remove from relationship_records storage
        // TODO: Implement N:N junction table logic
      }
    }),
    {
      name: 'record-storage'
    }
  )
);
```

### Migration Path from Current RecordTemplate to Object Model

#### Phase 1: Parallel Architecture (Week 1-2)

**Goal:** Introduce Object model without breaking existing RecordTemplate functionality

**Changes:**
1. Create new tables in Supabase: `objects`, `applications`, `records`, `relationship_records`
2. Create new stores: `objectStore`, `applicationStore` (keep existing `designStore`, `catalogStore`)
3. Create new pages: `/app-builder`, `/object-designer` (keep existing `/design`, `/define`)
4. Add "Migrate to Objects" button in existing projects

**Implementation:**
```typescript
// src/stores/objectStore.ts (new)
export const useObjectStore = create(...); // Full implementation above

// src/stores/designStore.ts (existing - unchanged)
export const useDesignStore = create(...); // Keep as-is for backwards compatibility

// src/pages/AppBuilder.tsx (new)
export function AppBuilder() {
  const { applications, createApplication } = useApplicationStore();
  const { objects } = useObjectStore();

  return (
    <div>
      <h1>Build Application</h1>
      <button onClick={() => createApplication({ name: 'My CRM', objects: [] })}>
        Create New Application
      </button>
      {/* App builder UI */}
    </div>
  );
}

// src/pages/Design.tsx (existing - add migration button)
export function Design() {
  const { activeProject } = useDesignStore();

  const handleMigrate = () => {
    // Convert RecordTemplate to Object
    const newObject = convertRecordTemplateToObject(activeProject);
    useObjectStore.getState().createObject(newObject);
  };

  return (
    <div>
      {/* Existing form designer UI */}
      <button onClick={handleMigrate} className="bg-blue-600">
        Migrate to Object-Based Architecture
      </button>
    </div>
  );
}
```

#### Phase 2: Migration Utility (Week 3)

**Goal:** Auto-convert existing RecordTemplate projects to Object model

**Converter Function:**
```typescript
// src/utils/migrations/recordTemplateToObject.ts

export function convertRecordTemplateToObject(project: Project): Object {
  // Convert form fields to object fields
  const fields: Field[] = project.schema.map(formField => ({
    id: `fld_${formField.id}`,
    name: formField.label,
    apiName: formField.name,
    type: mapFormTypeToFieldType(formField.type),
    required: formField.required || false,
    unique: false,
    config: convertFieldConfig(formField),
    helpText: formField.helpText,
    placeholder: formField.placeholder,
    readOnly: false,
    visibleToRoles: ['all'],
    editableByRoles: ['all']
  }));

  // Auto-generate default views
  const formView: FormView = {
    id: `form_default`,
    name: `${project.name} Form`,
    isDefault: true,
    sections: [
      {
        title: 'Information',
        columns: 2,
        fields: fields.map(f => f.id)
      }
    ],
    showRelatedLists: false
  };

  const tableView: TableView = {
    id: `table_default`,
    name: `All ${project.name}`,
    isDefault: true,
    columns: fields.map(f => ({
      fieldId: f.id,
      visible: true,
      locked: false
    })),
    pageSize: 25,
    enableInlineEdit: true,
    bulkActions: ['delete', 'export']
  };

  // Check if kanban view exists (groupByField)
  const kanbanField = fields.find(f => f.type === 'dropdown' && f.config.options);
  const kanbanView: KanbanView | null = kanbanField ? {
    id: `kanban_default`,
    name: `${project.name} Board`,
    isDefault: true,
    groupByField: kanbanField.id,
    columns: kanbanField.config.options!.map(opt => ({
      value: opt.value,
      label: opt.label,
      color: opt.color || '#3b82f6'
    })),
    cardTitleField: fields[0]?.id || '',
    cardFields: fields.slice(1, 4).map(f => f.id)
  } : null;

  // Create object
  const newObject: Object = {
    id: `obj_${project.id}`,
    name: project.name,
    pluralName: `${project.name}s`, // Simple pluralization
    description: '',
    icon: 'table',
    isCustom: true,
    fields,
    relationships: [], // No relationships in old model
    views: {
      forms: [formView],
      tables: [tableView],
      kanbans: kanbanView ? [kanbanView] : [],
      calendars: []
    },
    permissions: {
      create: ['all'],
      read: ['all'],
      update: ['all'],
      delete: ['all']
    },
    createdAt: project.createdAt,
    updatedAt: new Date().toISOString(),
    createdBy: 'user_migration'
  };

  return newObject;
}

function mapFormTypeToFieldType(formType: FieldType): FieldType {
  const typeMap: Record<string, FieldType> = {
    'text': 'text',
    'textarea': 'longtext',
    'email': 'email',
    'phone': 'phone',
    'url': 'url',
    'number': 'number',
    'money': 'currency',
    'date': 'date',
    'checkbox': 'checkbox',
    'select': 'dropdown',
    'radio': 'radio',
    'rating': 'number', // Convert rating to number
    'progress': 'percentage',
    'labels': 'multiselect',
    'users': 'user',
    'file': 'file'
  };

  return typeMap[formType] || 'text';
}

function convertFieldConfig(formField: any): FieldConfig {
  const config: FieldConfig = {};

  if (formField.options) {
    config.options = formField.options;
  }

  if (formField.min !== undefined) {
    config.min = formField.min;
  }

  if (formField.max !== undefined) {
    config.max = formField.max;
  }

  if (formField.maxLength) {
    config.maxLength = formField.maxLength;
  }

  if (formField.type === 'money') {
    config.currencySymbol = formField.currency || '$';
    config.decimals = 2;
  }

  return config;
}

// Migrate all existing projects
export function migrateAllProjects() {
  const { projects } = useDesignStore.getState();
  const { createObject } = useObjectStore.getState();

  projects.forEach(project => {
    const object = convertRecordTemplateToObject(project);
    createObject(object);
  });

  console.log(`Migrated ${projects.length} projects to objects`);
}
```

#### Phase 3: Deprecate Old Architecture (Week 4-5)

**Goal:** Phase out RecordTemplate, make Objects the default

**Changes:**
1. Redirect `/design` to `/app-builder`
2. Hide old "Create Project" flow
3. Show migration banner on old projects
4. Archive `designStore` (read-only mode)

**Banner Component:**
```typescript
// src/components/MigrationBanner.tsx
export function MigrationBanner({ projectId }: { projectId: string }) {
  const [migrated, setMigrated] = useState(false);

  const handleMigrate = () => {
    const { projects } = useDesignStore.getState();
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    const object = convertRecordTemplateToObject(project);
    useObjectStore.getState().createObject(object);

    setMigrated(true);
  };

  if (migrated) return null;

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-yellow-700">
            This project uses the old form-based architecture. Migrate to the new object-based architecture to unlock advanced features like relationships, multiple views, and more.
          </p>
          <button onClick={handleMigrate} className="mt-2 text-sm font-medium text-yellow-700 hover:text-yellow-600">
            Migrate Now →
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### Phase 4: Full Transition (Week 6+)

**Goal:** All users on Object-based architecture

**Changes:**
1. Remove `designStore` completely
2. Delete old `/design` page
3. Update all documentation
4. Archive old database tables (backup only)

---

## Critical Insights (Turkish)

### 1. Template-Centric vs Object-Centric: Temel Fark

**Template-Centric (Mevcut Yaklaşım):**
```
Kullanıcı düşüncesi: "Müşteri formu tasarlayacağım"
                     ↓
                 Form oluştur
                     ↓
               Alanlar ekle
                     ↓
         Table/Kanban otomatik oluşsun
                     ↓
                   BITTI

Sorun: Application = Tek bir form + otomatik görünümler
       Relationships yok, multi-object apps yapılamaz
```

**Object-Centric (Doğru Yaklaşım):**
```
Kullanıcı düşüncesi: "CRM uygulaması yapacağım"
                     ↓
          CRM'de ne var? → Contact, Company, Opportunity
                     ↓
         Her biri için Object oluştur
                     ↓
        Object'ler arası ilişkiler tanımla
                     ↓
       Her Object için görünümler oluştur
                     ↓
                  BITTI

Sonuç: Application = İlişkili Object'lerin koleksiyonu
       Esnek, genişletilebilir, gerçek uygulamalar
```

### 2. "Bir Uygulama Tasarlayacak Bir Yapıda Değiliz" - Neden Doğru?

**Şu an yapabildiğimiz:**
- Tek bir form tasarlamak (örn: "Müşteri Formu")
- O formun table/kanban görünümlerini göstermek
- Veriyi localStorage'da saklamak

**Yapamadığımız (ama yapılması gereken):**
- Birden fazla ilişkili object oluşturmak (Contact + Company + Opportunity)
- Object'ler arası relationships tanımlamak (Contact → Company: "Works at")
- Relationship'leri UI'da göstermek (Company sayfasında "Related Contacts" listesi)
- Complex queries (Tüm open opportunity'leri olan company'leri göster)
- Cross-object workflows (Opportunity Closed Won olunca, Contact'ı "Customer" olarak işaretle)

**Örnek: CRM vs Tek Form**

```
❌ Mevcut Yaklaşım: "Müşteri Formu"
   - Name, Email, Company, Phone fields
   - Table view ile listeleyebiliyorum
   - Kanban view ile status'e göre gruplayabiliyorum

   SORUN:
   - "Company" sadece text field, gerçek bir Company object'i değil
   - Company'nin kendi bilgileri yok (Industry, Revenue, etc.)
   - Bir Company'nin kaç müşterisi olduğunu göremiyorum
   - Opportunity ekleyemiyorum (farklı bir form olur, müşteriye link edemem)

✅ Doğru Yaklaşım: "CRM Application"
   - Contact Object (Name, Email, Phone) + Company (N:1 Lookup)
   - Company Object (Name, Industry, Revenue)
   - Opportunity Object (Title, Amount, Stage) + Contact (N:1) + Company (N:1)

   ÇÖZÜM:
   - Company sayfasını açınca, tüm Contacts'ı görebiliyorum (Related List)
   - Company sayfasında, tüm Opportunities'i görebiliyorum
   - Contact sayfasını açınca, hangi Company'de çalıştığını görebiliyorum (Lookup)
   - Opportunity sayfasını açınca, hem Contact hem Company'yi görebiliyorum
```

### 3. Flexibility Through Relationships (İlişkilerle Esneklik)

**Kuvvetli platformlar neden object-centric?**

Çünkü her şey relationships üzerine kurulu. Relationship olmadan, her object izole bir ada gibi kalır.

**Örnek: ITSM Uygulaması**

```
Incident Object:
- Fields: Number, Description, Priority, State
- Relationships:
  * Assigned To → User (N:1 Lookup)
  * Affected User → User (N:1 Lookup)
  * Related To → Configuration Item (N:1 Lookup)
  * Caused By → Problem (N:1 Lookup)
  * Resolved By → Change Request (N:N, junction table)

Bu relationships ile neler yapabilirsiniz?

1. User sayfasını açınca:
   - "Assigned Incidents" (bana atanan)
   - "Submitted Incidents" (benim açtığım)

2. Configuration Item sayfasını açınca:
   - "Related Incidents" (bu CI ile ilgili tüm hatalar)

3. Problem sayfasını açınca:
   - "Child Incidents" (bu problem'den kaynaklanan tüm hatalar)
   - Problem'i sil → Tüm child incidents silinsin (cascade delete)

4. Change Request sayfasını açınca:
   - "Resolved Incidents" (bu change ile çözülen hatalar)
   - N:N relationship → Bir change birden fazla incident çözebilir
```

**Mevcut yaklaşımla yapabilir miydiniz?**

Hayır. Çünkü:
- "Assigned To" sadece text field (gerçek User object'i değil)
- Related Lists yok (User → Incidents ilişkisini gösteremezsiniz)
- Cascade delete yok (Problem silinince incidents kalır)
- N:N relationships yok (Change ↔ Incidents junction table yok)

### 4. Object-First Approach'un Gerçek Gücü

**Scenario:** E-commerce platformu yapalım

```
Objects:
1. Customer
   - Fields: Name, Email, Phone, Address, Loyalty Points
   - Relationships:
     * Orders (1:N, customer has many orders)
     * Wishlisted Products (N:N, junction: customer_wishlists)

2. Product
   - Fields: Name, SKU, Price, Stock, Category
   - Relationships:
     * Category (N:1 Lookup)
     * Supplier (N:1 Lookup)
     * Reviews (1:N, product has many reviews)
     * Customers Who Wishlisted (N:N, inverse of Customer→Products)

3. Order
   - Fields: Order Number, Date, Total, Status, Shipping Address
   - Relationships:
     * Customer (N:1 Lookup, required)
     * Order Items (1:N, cascade delete)
     * Shipment (1:1, optional)

4. Order Item (Junction for Order ↔ Product)
   - Fields: Quantity, Unit Price, Discount
   - Relationships:
     * Order (N:1, master-detail)
     * Product (N:1 Lookup)

5. Category
   - Fields: Name, Description, Parent Category
   - Relationships:
     * Products (1:N)
     * Parent Category (N:1 self-referencing, for hierarchy)

6. Supplier
   - Fields: Name, Contact, Address, Rating
   - Relationships:
     * Products (1:N)
```

**Bu relationships ile yapabilecekleriniz:**

1. **Customer sayfası:**
   - Related Orders (tüm siparişleri)
   - Wishlisted Products (favori ürünleri)
   - Total Spent (rollup field: SUM of Order.Total)
   - Loyalty Tier (formula: if Total Spent > 1000 then "Gold" else "Silver")

2. **Product sayfası:**
   - Related Category (lookup ile kategori bilgisi)
   - Related Supplier (tedarikçi bilgisi)
   - Customer Reviews (1:N related list)
   - Average Rating (rollup: AVG of Review.Rating)
   - Customers Who Wishlisted (N:N, kaç kişi favori eklemiş)

3. **Order sayfası:**
   - Related Customer (lookup ile müşteri bilgisi)
   - Order Items (alt tablo, her satır bir ürün)
   - Total Calculated (formula: SUM of OrderItem.Quantity * OrderItem.UnitPrice)
   - Shipment Status (1:1 relationship ile kargo bilgisi)

4. **Category sayfası:**
   - Parent Category (self-referencing lookup ile hiyerarşi)
   - Child Categories (1:N self-referencing)
   - Products in Category (1:N related list)
   - Total Products (rollup: COUNT of Products)

**Template-centric approach ile bu yapabilir miydiniz?**

HAYIR. Çünkü:
- Her object izole bir form olurdu
- Order → OrderItem relationship yok (master-detail cascade delete)
- Product → Category sadece text olurdu (gerçek lookup değil)
- N:N relationships yok (Customer ↔ Product wishlist junction table yok)
- Self-referencing relationships yok (Category → Parent Category)
- Rollup/Formula fields yok (Total Spent, Average Rating hesaplaması)

### 5. Platform Büyükleri Neden Bu Yaklaşımı Kullanıyor?

**ServiceNow:**
- 20+ yıldır ITSM lideri
- Her şey Table (Object)
- 500+ pre-built tables (Incident, Problem, Change, Asset, User, etc.)
- Enterprise customers için %100 customizable
- Relationships ile karmaşık workflows (Incident → Problem → Change → CI)

**Salesforce:**
- CRM pazarının %20'si (1 numaralı oyuncu)
- Object-oriented architecture (sObject model)
- Standard objects (Account, Contact, Lead, Opportunity)
- Custom objects (herkes kendi industry'sine özel objects yaratır)
- Relationships = CRM'in temeli (Account → Contacts → Opportunities)

**Airtable:**
- En user-friendly no-code platform
- Base → Table → Linked Records → Views
- Kullanıcılar dakikalar içinde karmaşık apps yapıyor (project management, CRM, inventory)
- Relationship'ler o kadar kolay ki, spreadsheet bilgisiyle yapılıyor

**HubSpot:**
- SMB CRM'de lider
- Standard Objects + Custom Objects
- Associations (labeled relationships: "Manager of", "Works at")
- 2026 trend: N:N associations with custom labels

**Microsoft Dataverse:**
- Power Platform'un foundation'ı
- 400+ standard tables (Account, Contact, etc.)
- Low-code + pro-code (Power Apps + Power Automate)
- Relationships ile enterprise apps (HR onboarding, supply chain, etc.)

**Ortak Patern:**
```
Workspace → Application → Objects → Relationships → Views → Data
```

Hiçbiri "form tasarla, otomatik table oluşsun" yaklaşımı kullanmıyor. Hepsi:
1. Object oluştur
2. Relationships tanımla
3. Views oluştur (form, table, kanban, etc.)
4. Data gir

---

## Sonuç: Yol Haritası

### Mevcut Durum (Template-Centric)
```
✅ Yapabildiğimiz:
- Basit form tasarlamak
- Table/Kanban view otomatik oluşturmak
- localStorage'da veri saklamak
- Field validation

❌ Yapamadığımız:
- Birden fazla ilişkili object oluşturmak
- Relationships tanımlamak
- Related lists göstermek
- Complex queries
- Cascade behaviors
- Gerçek uygulamalar (CRM, ITSM, ERP)
```

### Hedef Durum (Object-Centric)
```
✅ Yapacağımız:
1. Object Definition System
   - Object oluşturma (name, plural, icon, fields)
   - Field types (30+ type: text, number, lookup, formula, rollup, etc.)
   - Field validation (required, unique, min/max, regex)

2. Relationship System
   - Lookup (N:1)
   - One-to-Many (1:N with cascade)
   - Many-to-Many (N:N with junction table)
   - Self-referencing (hierarchies)
   - Labeled relationships ("Works at", "Manager of")

3. Multi-View System
   - Form views (multiple layouts per object)
   - Table views (filterable, sortable, with saved views)
   - Kanban views (by any dropdown field)
   - Calendar views (by date fields)
   - Related lists (show related records)
   - Dashboards (charts, KPIs, reports)

4. Application Builder
   - Create applications (collection of objects)
   - Define navigation menu
   - Configure permissions (object-level, field-level)
   - Publish/deploy

5. Advanced Features
   - Formula fields (calculated values)
   - Rollup fields (aggregate from related records)
   - Validation rules (cross-field validation)
   - Workflows (trigger actions on record changes)
   - APIs (REST API for all objects)
```

### İmplementasyon Zaman Çizelgesi

**Week 1-2: Parallel Architecture**
- Object model oluştur (types, stores, database schema)
- Object designer UI (field editor, relationship editor)
- Eski RecordTemplate'i koruyarak yeni sistem ekle

**Week 3: Migration Utility**
- Auto-convert RecordTemplate → Object
- Migration banner (eski projelerde göster)
- Batch migration script

**Week 4-5: Deprecation**
- Object-based flow'u default yap
- Eski design page'i redirect et
- Documentation update

**Week 6+: Full Transition**
- RecordTemplate'i tamamen kaldır
- Object-centric documentation
- Advanced features (formula, rollup, workflows)

### Final Tavsiye

**Şimdi yapılması gereken:**
1. ✅ Bu research'ü oku ve karar ver: Object-centric mi, yoksa template-centric mi devam?
2. ✅ Eğer object-centric → Migration plan'ı başlat (Week 1-2)
3. ✅ Eğer template-centric → Farkında ol ki: Sadece basit form-based apps yapabilirsin, CRM/ITSM/ERP gibi complex apps yapılamaz

**Uzun vadede:**
- Object-centric → Salesforce, ServiceNow, Airtable seviyesinde bir platform
- Template-centric → Sadece Google Forms seviyesinde bir form builder

**Platform büyükleri 20 yıldır object-centric kullanıyor. Bunun bir sebebi var.**

---

**Document Status:** ✅ Complete
**Last Updated:** 17 Ocak 2026
**Next Steps:** Review + Decision + Migration Planning
