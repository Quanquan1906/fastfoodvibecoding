# 📊 LESSON 3: VISUAL SUMMARY & CHECKLISTS

## 🎯 ARCHITECTURE LAYERS - ONE-PAGE VISUAL

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    FastAPI Backend + React Frontend                      ║
║                                                                          ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │                   PRESENTATION LAYER                           │   ║
║  │  (What people see & interact with)                             │   ║
║  │                                                                 │   ║
║  │  Backend:                          Frontend:                    │   ║
║  │  • FastAPI Routes                  • React Pages                │   ║
║  │  • WebSocket Handlers              • React Components           │   ║
║  │  • Request Parsing                 • User Actions               │   ║
║  │  • Response Formatting             • Event Handlers             │   ║
║  │                                                                 │   ║
║  │  Responsibility: HTTP ↔ Logic Interface                         │   ║
║  │  Size: ~5-10 lines per endpoint                                │   ║
║  └──────────────────────┬────────────────────────────────────────┘   ║
║                         ↓ (calls)                                     ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │                   APPLICATION LAYER                            │   ║
║  │  (Where the real work happens)                                 │   ║
║  │                                                                 │   ║
║  │  Backend:                          Frontend:                    │   ║
║  │  • Use Cases                       • Custom Hooks                │   ║
║  │  • Business Rules                  • Business Logic              │   ║
║  │  • Validation                      • State Management            │   ║
║  │  • Orchestration                   • Data Transformation         │   ║
║  │                                                                 │   ║
║  │  Responsibility: Logic Execution                                │   ║
║  │  Size: ~20-50 lines per use case                               │   ║
║  └──────────────────────┬────────────────────────────────────────┘   ║
║                         ↓ (uses)                                      ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │                      DATA LAYER                                │   ║
║  │  (How we store & get data)                                     │   ║
║  │                                                                 │   ║
║  │  Backend:                          Frontend:                    │   ║
║  │  • Repositories                    • API Clients                 │   ║
║  │  • Database Queries                • WebSocket Manager           │   ║
║  │  • Adapters (Cloudinary, Stripe)   • Local Storage               │   ║
║  │  • Data Serialization              • Cache Management            │   ║
║  │                                                                 │   ║
║  │  Responsibility: Data Persistence & Retrieval                  │   ║
║  │  Size: ~10-20 lines per repository                             │   ║
║  └──────────────────────┬────────────────────────────────────────┘   ║
║                         ↓ (accesses)                                  ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │               EXTERNAL SERVICES                                │   ║
║  │  (The rest of the internet)                                    │   ║
║  │                                                                 │   ║
║  │  Backend:                          Frontend:                    │   ║
║  │  • MongoDB (database)              • localhost:3000 server       │   ║
║  │  • Cloudinary (images)             • Backend API                 │   ║
║  │  • Stripe (payments)               • WebSocket server            │   ║
║  │                                                                 │   ║
║  │  Responsibility: External Reality                              │   ║
║  └─────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 FOLDER STRUCTURE - WHAT GOES WHERE

```
┌─────────────────────────────────────────────────┐
│   PRESENTATION LAYER                            │
├─────────────────────────────────────────────────┤
│ Where: app/presentation/                        │
│ Files:                                          │
│   routers/                                      │
│   ├─ order_router.py (order endpoints)          │
│   ├─ auth_router.py (login endpoints)           │
│   ├─ restaurant_router.py (REST endpoints)      │
│   └─ ...                                        │
│   websocket/                                    │
│   ├─ order_tracking.py (WebSocket endpoints)    │
│   └─ manager.py (WebSocket connections)         │
│   dependencies.py (FastAPI Depends)             │
│                                                 │
│ Pattern: @router.post("/api/...")               │
│ Depth: 5-10 lines per endpoint                  │
│ Rule: Don't touch database!                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   APPLICATION LAYER                             │
├─────────────────────────────────────────────────┤
│ Where: app/application/                         │
│ Files:                                          │
│   use_cases/                                    │
│   ├─ order_use_case.py (order business logic)   │
│   ├─ auth_use_case.py (auth logic)              │
│   ├─ payment_use_case.py (payment logic)        │
│   └─ ...                                        │
│   dto/                                          │
│   ├─ order_dto.py (request/response models)     │
│   ├─ auth_dto.py                                │
│   └─ ...                                        │
│   interfaces/                                   │
│   ├─ repository.py (IRepository interface)      │
│   ├─ storage_adapter.py (IStorageAdapter)       │
│   └─ payment_gateway.py (IPaymentGateway)       │
│   services/                                     │
│   └─ (use_cases ARE the services)               │
│                                                 │
│ Pattern: class OrderUseCase:                    │
│ Depth: 20-50 lines per use case                 │
│ Rule: NO database direct access!                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   DATA LAYER                                    │
├─────────────────────────────────────────────────┤
│ Where: app/data/                                │
│ Files:                                          │
│   repositories/                                 │
│   ├─ base_repository.py (abstract base)         │
│   ├─ order_repository.py (order DB access)      │
│   ├─ user_repository.py (user DB access)        │
│   └─ ...                                        │
│   adapters/                                     │
│   ├─ cloudinary_adapter.py (image uploads)      │
│   ├─ payment_adapter.py (payment processing)    │
│   ├─ email_adapter.py (email sending)           │
│   └─ ...                                        │
│   database.py (MongoDB connection)              │
│   models/ (domain models)                       │
│   ├─ order.py                                   │
│   ├─ user.py                                    │
│   └─ ...                                        │
│                                                 │
│ Pattern: async def create(self, data)           │
│ Depth: 10-20 lines per repository               │
│ Rule: ONLY database operations here!            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   SHARED UTILITIES                              │
├─────────────────────────────────────────────────┤
│ Where: app/shared/                              │
│ Files:                                          │
│   exceptions.py (custom errors)                 │
│   constants.py (app constants)                  │
│   utils.py (helper functions)                   │
│   validators.py (validation logic)              │
│                                                 │
│ Use: From any layer                             │
└─────────────────────────────────────────────────┘
```

---

## ✅ PHASE-BY-PHASE IMPLEMENTATION CHECKLIST

### PHASE 1: CREATE STRUCTURE ⏱️ 1-2 hours

```
BEFORE STARTING:
□ Backup current code (git commit)
□ Create new branch: git checkout -b lesson3-3tier-refactor
□ Read LESSON3_QUICK_REFERENCE.md

EXECUTE:
□ Create app/presentation/
  □ Create routers/ subfolder
  □ Create websocket/ subfolder
  □ Create dependencies.py
  □ Create __init__.py files

□ Create app/application/
  □ Create use_cases/ subfolder
  □ Create dto/ subfolder
  □ Create interfaces/ subfolder
  □ Create __init__.py files

□ Create app/data/
  □ Create repositories/ subfolder
  □ Create adapters/ subfolder
  □ Create __init__.py files

□ Create app/shared/
  □ Create __init__.py

VERIFY:
□ Folder structure matches LESSON3_QUICK_REFERENCE.md
□ All __init__.py files exist
□ No code moved yet (just folders)
```

### PHASE 2: CREATE BASE ABSTRACTIONS ⏱️ 2-3 hours

```
CREATE EXCEPTIONS:
□ File: app/shared/exceptions.py
  □ ApplicationException
  □ ValidationException
  □ BusinessRuleException
  □ ResourceNotFoundException
  □ StorageException
  □ PaymentException

CREATE INTERFACES:
□ File: app/data/repositories/base_repository.py
  □ Abstract methods: create, get_by_id, get_all, update, delete

□ File: app/application/interfaces/storage_adapter.py
  □ Abstract methods: upload_image, delete_image

□ File: app/application/interfaces/payment_gateway.py
  □ Abstract methods: process_payment, refund_payment

VERIFY:
□ All interfaces have @abstractmethod decorators
□ All exceptions inherit from ApplicationException
□ Code follows PEP 8
```

### PHASE 3: REFACTOR ORDERS ⏱️ 3-4 hours

```
DATA LAYER:
□ Create: app/data/repositories/order_repository.py
  □ Inherit from BaseRepository
  □ Implement: create, get_by_id, get_all, update, delete
  □ Add: get_by_customer_id, get_by_restaurant_id, update_status, assign_drone
  □ Add: _serialize method (ObjectId → string id)
  
APPLICATION LAYER:
□ Create: app/application/dto/order_dto.py
  □ OrderCreateDTO (request model)
  □ OrderResponseDTO (response model)
  □ OrderItemDTO (line items)

□ Create: app/application/use_cases/order_use_case.py
  □ Inject OrderRepository, RestaurantRepository, MenuRepository, DroneRepository
  □ Method: create_order (with ALL business rules)
  □ Method: get_order
  □ Method: get_customer_orders
  □ Method: update_order_status
  □ Method: assign_drone_to_order

PRESENTATION LAYER:
□ Create: app/presentation/routers/order_router.py
  □ POST /api/orders (create)
  □ GET /api/orders/{id} (get)
  □ GET /api/orders/customer/{customer_id} (list by customer)
  □ PATCH /api/orders/{id}/status (update status)
  □ POST /api/orders/{id}/assign-drone (assign drone)
  □ Catch exceptions and convert to HTTPException

DEPENDENCIES:
□ Update: app/presentation/dependencies.py
  □ Provide: get_order_repo()
  □ Provide: get_restaurant_repo()
  □ Provide: get_menu_repo()
  □ Provide: get_drone_repo()
  □ Provide: get_order_use_case (with all deps injected)

INTEGRATION:
□ Update: main.py
  □ Remove old order routes
  □ Include new order router

TESTING:
□ Test all order endpoints manually
□ Verify: Create order works
□ Verify: Get order works
□ Verify: List orders works
□ Verify: Update status works
□ Verify: Assign drone works
□ Check: No functionality broken
```

### PHASE 4-8: REFACTOR OTHER DOMAINS ⏱️ 12-16 hours

Repeat Phase 3 for each domain:

```
DOMAIN 1: AUTH
□ Create: AuthRepository
□ Create: AuthUseCase
□ Create: AuthRouter
□ Create: AuthDTO
□ Update: dependencies.py
□ Test all endpoints

DOMAIN 2: RESTAURANT
□ Create: RestaurantRepository
□ Create: RestaurantUseCase
□ Create: RestaurantRouter
□ Create: RestaurantDTO
□ Update: dependencies.py
□ Test all endpoints

DOMAIN 3: MENU
□ Create: MenuRepository
□ Create: MenuUseCase
□ Create: MenuRouter
□ Create: MenuDTO
□ Update: dependencies.py
□ Test all endpoints

DOMAIN 4: DRONE
□ Create: DroneRepository
□ Create: DroneUseCase
□ Create: DroneRouter
□ Create: DroneDTO
□ Update: dependencies.py
□ Test all endpoints

DOMAIN 5: PAYMENT
□ Create: PaymentRepository
□ Create: PaymentUseCase
□ Create: PaymentRouter
□ Create: PaymentDTO
□ Update: dependencies.py
□ Test all endpoints
```

### PHASE 9: FRONTEND REFACTOR ⏱️ 2-3 hours

```
CREATE INFRASTRUCTURE LAYER:
□ Create: src/infrastructure/api/
  □ client.js (Axios configuration)
  □ order_client.js (order API calls)
  □ restaurant_client.js (restaurant API calls)
  □ auth_client.js (auth API calls)
  □ user_client.js (user API calls)

CREATE PRESENTATION LAYER:
□ Create: src/presentation/hooks/
  □ useOrder.js (order business logic)
  □ useRestaurant.js (restaurant logic)
  □ useAuth.js (auth logic)

UPDATE COMPONENTS:
□ Remove API calls from components
□ Use custom hooks instead
□ Pass data as props
□ Keep components pure (UI only)

VERIFY:
□ No API calls in components
□ All API calls in infrastructure/
□ Business logic in hooks
□ Components are dumb (UI only)
```

### PHASE 10: TESTING & CLEANUP ⏱️ 1-2 hours

```
TESTING:
□ Test all endpoints thoroughly
□ Test all business rules
□ Test error cases
□ Test edge cases

CLEANUP:
□ Remove old app/api/routes.py
□ Remove old app/services/ (if separate)
□ Remove old React API calls from components
□ Update imports in main.py

VERIFICATION:
□ No errors in terminal
□ All tests pass
□ No functionality broken
□ Code follows PEP 8
□ Frontend and backend work together

COMMIT:
□ Git add .
□ Git commit -m "Lesson 3: Refactor into 3-tier architecture"
□ Git push origin lesson3-3tier-refactor
```

---

## 🎯 DO'S AND DON'TS

### ✅ DO

```
✅ Router:
  □ Parse and validate request
  □ Call use case
  □ Catch exceptions
  □ Return HTTP response

✅ Use Case:
  □ Execute business logic
  □ Validate business rules
  □ Call repositories
  □ Call adapters
  □ Raise custom exceptions

✅ Repository:
  □ Query database only
  □ Serialize results
  □ Raise data exceptions

✅ Adapter:
  □ Call external API only
  □ Handle API-specific logic
  □ Raise storage exceptions

✅ Dependency Injection:
  □ Pass dependencies to constructors
  □ Use FastAPI Depends()
  □ Mock in tests
```

### ❌ DON'T

```
❌ Router:
  □ Don't access database directly
  □ Don't contain business logic
  □ Don't call external APIs
  □ Don't import other routers
  □ Don't raise HTTPException in use cases

❌ Use Case:
  □ Don't access database directly (use repositories)
  □ Don't call external APIs directly (use adapters)
  □ Don't handle HTTP requests
  □ Don't render UI
  □ Don't raise HTTPException

❌ Repository:
  □ Don't contain business logic
  □ Don't call external APIs
  □ Don't import routers
  □ Don't raise HTTPException

❌ Dependency Injection:
  □ Don't create instances in use case __init__
  □ Don't use global instances
  □ Don't create circular dependencies
  □ Don't use get_db() outside repositories
```

---

## 📊 PROGRESS TRACKER

### Week 1
- [ ] Day 1: Read documentation (Phase 1)
- [ ] Day 2-3: Create structure & foundations (Phases 1-2)
- [ ] Day 4-5: Refactor Orders (Phase 3)

### Week 2
- [ ] Day 1-3: Refactor Auth, Restaurant (Phases 4-5)
- [ ] Day 4-5: Refactor Menu, Drone (Phases 6-7)

### Week 3
- [ ] Day 1: Refactor Payment (Phase 8)
- [ ] Day 2: Frontend refactor (Phase 9)
- [ ] Day 3-5: Testing & cleanup (Phase 10)

---

## 🚦 QUALITY GATES

Before moving to next phase, verify:

```
✅ Code Quality
  □ No linting errors (flake8)
  □ Follows PEP 8
  □ Type hints present
  □ Docstrings complete

✅ Testing
  □ All endpoints tested
  □ Business rules validated
  □ Error cases handled
  □ Edge cases covered

✅ Functionality
  □ No existing features broken
  □ All endpoints work
  □ Data persists correctly
  □ Frontend/Backend communicate

✅ Architecture
  □ No circular dependencies
  □ No cross-layer violations
  □ Dependencies injected properly
  □ Interfaces used consistently
```

---

## 💡 FINAL CHECKLIST

Before calling this complete:

```
ARCHITECTURE:
□ 3 clear layers created
□ No backward dependencies
□ All dependencies injected
□ Interfaces used for external services

IMPLEMENTATION:
□ All domains refactored
□ All repositories created
□ All use cases created
□ All routers created
□ All DTOs created
□ All adapters created

TESTING:
□ Unit tests written
□ Integration tests written
□ API tests written
□ All tests passing
□ Code coverage 80%+

DOCUMENTATION:
□ Code comments added
□ README updated
□ Folder structure documented
□ Dependencies documented

CLEANUP:
□ Old code removed
□ Imports updated
□ No warnings in logs
□ Git commits clear and meaningful
```

---

## 🎉 YOU'RE DONE!

When all checkboxes are checked:
✅ You've successfully implemented 3-tier architecture
✅ Your codebase is now scalable
✅ Your team can move faster
✅ Your code is maintainable

**Next Step:** Start Lesson 4 - Caching with Redis

