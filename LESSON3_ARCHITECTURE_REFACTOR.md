# Lesson 3: 3-Tier Architecture Refactoring Guide

**Objective:** Refactor the FastFood delivery system into a clean, decoupled 3-layer architecture (Presentation → Application → Data).

---

## 📊 TARGET ARCHITECTURE OVERVIEW

```
3-Tier Architecture:
┌──────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Controllers/Routers/UI)     │
│  - FastAPI routers / WebSocket endpoints         │
│  - React pages/components                        │
│  - NO business logic here                        │
└──────────────────────────────────────────────────┘
                        ↓ (depends on)
┌──────────────────────────────────────────────────┐
│ APPLICATION LAYER (Business Logic/Use Cases)     │
│  - Services (OrderUseCase, PaymentUseCase, etc)  │
│  - Domain objects & Entities                     │
│  - Use case orchestration                        │
└──────────────────────────────────────────────────┘
                        ↓ (depends on)
┌──────────────────────────────────────────────────┐
│ DATA LAYER (Persistence/External Services)       │
│  - Repositories (OrderRepository, etc)           │
│  - Adapters (CloudinaryAdapter, PaymentGateway)  │
│  - Direct DB access & external API calls         │
└──────────────────────────────────────────────────┘
```

---

## 📁 BACKEND FOLDER STRUCTURE

### NEW STRUCTURE (3-Tier)

```
backend/
├── main.py                           # Entry point (unchanged)
├── requirements.txt
├── .env
├── .gitignore
│
├── app/
│   ├── __init__.py
│   │
│   ├── presentation/                  ⭐ LAYER 1: PRESENTATION
│   │   ├── __init__.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth_router.py        # Login, register endpoints
│   │   │   ├── restaurant_router.py  # Restaurant CRUD
│   │   │   ├── menu_router.py        # Menu item CRUD
│   │   │   ├── order_router.py       # Order creation, listing
│   │   │   ├── drone_router.py       # Drone management
│   │   │   └── admin_router.py       # Admin operations
│   │   ├── websocket/
│   │   │   ├── __init__.py
│   │   │   ├── order_tracking.py     # WebSocket endpoints
│   │   │   └── manager.py            # Connection manager (unchanged)
│   │   └── dependencies.py           # FastAPI Depends() providers
│   │
│   ├── application/                   ⭐ LAYER 2: APPLICATION (Business Logic)
│   │   ├── __init__.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── order_use_cases.py    # Order business logic
│   │   │   ├── payment_use_cases.py  # Payment logic
│   │   │   ├── auth_use_cases.py     # Auth logic
│   │   │   ├── restaurant_use_cases.py
│   │   │   └── drone_use_cases.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py      # Orchestrates repositories
│   │   │   ├── payment_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── restaurant_service.py
│   │   │   └── drone_service.py
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── order_dto.py          # Data Transfer Objects
│   │   │   ├── payment_dto.py
│   │   │   └── user_dto.py
│   │   └── interfaces/               # Abstractions
│   │       ├── __init__.py
│   │       ├── repository.py         # Base repo interface
│   │       ├── storage_adapter.py    # Abstract storage (Cloudinary, etc)
│   │       └── payment_gateway.py    # Abstract payment processor
│   │
│   ├── data/                          ⭐ LAYER 3: DATA (Persistence)
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py    # Abstract base
│   │   │   ├── order_repository.py   # MongoDB order queries
│   │   │   ├── user_repository.py
│   │   │   ├── restaurant_repository.py
│   │   │   ├── menu_item_repository.py
│   │   │   └── drone_repository.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── cloudinary_adapter.py # Cloudinary integration
│   │   │   ├── payment_adapter.py    # Payment gateway integration
│   │   │   └── email_adapter.py      # (Future) Email service
│   │   ├── database.py               # MongoDB connection (unchanged)
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── order.py              # Domain models
│   │       ├── user.py
│   │       ├── restaurant.py
│   │       ├── menu_item.py
│   │       └── drone.py
│   │
│   └── shared/                        ⭐ SHARED (Used by all layers)
│       ├── __init__.py
│       ├── exceptions.py             # Custom exceptions
│       ├── utils.py                  # Utilities
│       └── constants.py              # Constants
│
├── tests/                             (Optional: Mirror layer structure)
│   ├── unit/
│   │   ├── test_order_use_case.py
│   │   └── test_payment_use_case.py
│   └── integration/
│       └── test_order_repository.py
│
└── core/
    └── config.py                     # Environment & config
```

---

## 📱 FRONTEND FOLDER STRUCTURE

### NEW STRUCTURE (Presentation + Infrastructure)

```
frontend/
├── package.json
├── README.md
│
├── public/
│   ├── index.html
│   └── manifest.json
│
├── src/
│   ├── index.js
│   ├── App.js
│   │
│   ├── presentation/                  ⭐ LAYER 1: PRESENTATION (UI)
│   │   ├── __init__.js
│   │   ├── pages/
│   │   │   ├── Login.jsx             # No API calls here
│   │   │   ├── customer/
│   │   │   │   ├── Home.jsx          # Uses services
│   │   │   │   ├── Checkout.jsx
│   │   │   │   ├── Orders.jsx
│   │   │   │   └── TrackOrder.jsx
│   │   │   ├── restaurant/
│   │   │   │   └── Dashboard.jsx
│   │   │   └── admin/
│   │   │       └── AdminDashboard.jsx
│   │   ├── components/               # Reusable UI components
│   │   │   ├── DroneMap.jsx          # Pure UI component
│   │   │   ├── OrderCard.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       ├── Modal.jsx
│   │   │       └── Loading.jsx
│   │   └── hooks/
│   │       ├── useAuth.js            # Custom hook for auth context
│   │       ├── useOrder.js
│   │       └── useWebSocket.js
│   │
│   ├── infrastructure/                ⭐ LAYER 2: INFRASTRUCTURE (API/WS Clients)
│   │   ├── api/
│   │   │   ├── client.js             # Axios instance
│   │   │   ├── order_client.js       # Order API calls
│   │   │   ├── restaurant_client.js
│   │   │   ├── auth_client.js
│   │   │   ├── user_client.js
│   │   │   └── admin_client.js
│   │   ├── websocket/
│   │   │   ├── connection.js         # WebSocket manager
│   │   │   └── listeners.js          # Event listeners
│   │   ├── context/
│   │   │   ├── AuthContext.js        # Auth state
│   │   │   └── AppContext.js         # Global state
│   │   └── config.js                 # API base URL, constants
│   │
│   ├── domain/                        ⭐ LAYER 3: DOMAIN (Business Logic - Minimal)
│   │   ├── models.js                 # Domain entities
│   │   ├── validators.js             # Business rules
│   │   └── utils.js                  # Business utilities
│   │
│   ├── styles/
│   │   ├── App.css
│   │   ├── index.css
│   │   └── variables.css             # Color, spacing constants
│   │
│   └── utils/
│       ├── helpers.js                # General utilities
│       ├── constants.js              # App constants
│       └── formatters.js             # Data formatting
```

---

## ⭐ KEY PRINCIPLES APPLIED

### 1. **Separation of Concerns**
- **Presentation:** Only UI rendering & user input
- **Application:** Business logic, validation, orchestration
- **Data:** Database queries, external API calls

### 2. **Decoupling**
- Services depend on abstract repositories via dependency injection
- External services (Cloudinary) accessed through adapters
- No direct database access from routers/pages

### 3. **Dependency Inversion**
```
❌ WRONG (Tight Coupling):
RouterService → OrderRepository → MongoDB

✅ RIGHT (Decoupled):
Router → UseCase → IOrderRepository (interface) → OrderRepository → MongoDB
```

### 4. **Testability**
- Mock repositories and adapters easily
- Test business logic independently
- No need to spin up DB for unit tests

---

## 🔄 DATA FLOW EXAMPLE: Creating an Order

```
PRESENTATION LAYER:
┌─────────────────────────────────────────┐
│ POST /api/orders (Order Router)          │
│ - Parse request body                     │
│ - Validate input (Pydantic model)        │
│ - Call use case via Depends()            │
└─────────────────────────────────────────┘
                 ↓
APPLICATION LAYER:
┌─────────────────────────────────────────┐
│ OrderUseCase.create_order()              │
│ - Validate business rules                │
│ - Check inventory, pricing, auth         │
│ - Orchestrate repositories               │
│ - Return DTO                             │
└─────────────────────────────────────────┘
                 ↓
DATA LAYER:
┌─────────────────────────────────────────┐
│ OrderRepository.save()                   │
│ - Insert into MongoDB                    │
│ - Return saved entity                    │
└─────────────────────────────────────────┘
                 ↓
                RESPONSE
            (Order created)
```

---

## 🏗️ ARCHITECTURE BENEFITS

| Aspect | Benefit |
|--------|---------|
| **Decoupling** | Swap MongoDB for PostgreSQL by just replacing repository |
| **Testability** | Mock repositories → unit test services without DB |
| **Maintainability** | Clear responsibility → easier to locate & fix bugs |
| **Scalability** | Add new features without touching existing code |
| **Team Collaboration** | Different teams can work on different layers |
| **Code Reuse** | Services reused across routers & WebSocket handlers |

---

## 🚀 IMPLEMENTATION STRATEGY

### Phase 1: Create New Layer Structure
- Create folders: `presentation/`, `application/`, `data/`
- Keep old code alongside temporarily

### Phase 2: Create Interfaces & Base Classes
- `IOrderRepository` (abstract)
- `IStorageAdapter` (abstract)
- Start with one service

### Phase 3: Refactor One Domain (e.g., Orders)
- Create `order_repository.py` (data)
- Create `order_use_case.py` (application)
- Create `order_router.py` (presentation)
- Test thoroughly

### Phase 4: Refactor Remaining Domains
- Repeat for auth, payment, drone, etc.

### Phase 5: Cleanup
- Remove old files
- Update imports in `main.py`

---

## 📝 NEXT SECTIONS

See the refactored code examples below:
1. Repository Pattern (OrderRepository)
2. Adapter Pattern (CloudinaryAdapter)
3. Use Case / Service Layer (OrderUseCase)
4. Router/Controller (OrderRouter)
5. WebSocket Endpoint (OrderTrackingWS)
6. Frontend Service + Component Example

