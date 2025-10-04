# Gold Jewelry Business Management System - ER Diagram (Simplified)

## Entity Relationship Diagram

```mermaid
erDiagram
    USERS {
        int user_id PK
        string username
        string password_hash
        string full_name
        string email
        string phone
        enum user_type "admin|staff"
        datetime created_at
        boolean is_active
    }

    GOLD_INVENTORY {
        int inventory_id PK
        int gold_type_id FK
        decimal weight_grams
        decimal purity_percentage
        enum form "bar|coin|scrap|sheet"
        string description
        datetime received_date
        string supplier_info
        boolean is_available
    }

    GOLD_TYPES {
        int gold_type_id PK
        string name "24K|22K|18K|etc"
        decimal purity_percentage
        string description
    }

    FREELANCERS {
        int freelancer_id PK
        string full_name
        string specialization
        string phone
        string address
        string bank_details
        datetime joined_date
        boolean is_active
    }

    WORK_ORDERS {
        int work_order_id PK
        int freelancer_id FK
        int gold_type_id FK
        string jewelry_design
        decimal gold_weight_issued
        decimal expected_final_weight
        datetime issue_date
        datetime expected_completion_date
        enum status "issued|in_progress|completed"
        string special_instructions
        decimal wastage_weight
        decimal final_jewelry_weight
        datetime completion_date
        string notes
    }

    DESIGNS {
        int design_id PK
        string design_name
        string design_code
        string category "necklace|ring|earring|bracelet"
        string complexity_level "simple|medium|complex"
        decimal estimated_gold_weight
        string design_specifications
        boolean is_active
    }

    WORK_ORDER_DESIGNS {
        int work_order_design_id PK
        int work_order_id FK
        int design_id FK
        int quantity
        string custom_modifications
    }

    SUPPLIERS {
        int supplier_id PK
        string supplier_name
        string contact_person
        string phone
        string email
        string address
        string gst_number
        boolean is_active
    }

    GOLD_PURCHASES {
        int purchase_id PK
        int supplier_id FK
        int gold_type_id FK
        decimal weight_grams
        decimal purity_percentage
        datetime purchase_date
        string invoice_number
        string notes
    }

    GOLD_TYPES ||--o{ GOLD_INVENTORY : "categorizes"
    GOLD_TYPES ||--o{ WORK_ORDERS : "used_in"
    GOLD_TYPES ||--o{ GOLD_PURCHASES : "purchased"
    FREELANCERS ||--o{ WORK_ORDERS : "receives_work"
    WORK_ORDERS ||--o{ WORK_ORDER_DESIGNS : "includes"
    DESIGNS ||--o{ WORK_ORDER_DESIGNS : "specified_in"
    SUPPLIERS ||--o{ GOLD_PURCHASES : "supplies"
```

## Key Features & Workflows:

### 1. Gold Inventory Management
- Manual entry of gold quantities by type and purity
- Track available vs. allocated gold
- Record gold purchases from suppliers

### 2. Freelancer Work Management
- Issue work orders with specific gold quantities
- Track work progress and completion
- Monitor gold wastage within each order

### 3. Jewelry Production Tracking
- Track gold weight issued vs. final jewelry weight
- Calculate wastage for each work order
- Simple status tracking (issued, in progress, completed)

### 4. Design Management
- Maintain jewelry design catalog
- Track design complexity and estimated gold requirements

### 5. Monthly Reporting
- Gold inventory status
- Work order completion summary
- Freelancer performance metrics
- Wastage analysis

## Simplified Business Rules:
- **Gold-based transactions only** (no currency)
- **Wastage tracked within work orders** (e.g., 100gm issued, 2gm waste, 98gm final)
- **No gold returns** (direct inventory updates)
- **Offline operation** with local SQLite database
- **Monthly reporting** for business insights

This simplified design focuses on your core needs: tracking gold inventory, managing work orders, and monitoring production efficiency.
