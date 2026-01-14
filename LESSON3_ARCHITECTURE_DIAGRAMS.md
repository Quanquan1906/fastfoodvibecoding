# Lesson 3: Architecture Diagrams & Visual Guide

## 🏗️ SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ React Browser / Mobile Client                            │  │
│  │  - UI Components                                         │  │
│  │  - Pages                                                 │  │
│  │  - WebSocket Connection                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    (REST API + WebSocket)
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                     BACKEND SERVER (FastAPI)                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │        PRESENTATION LAYER (Controllers/Routers)        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │    │
│  │  │ AuthRouter   │  │ OrderRouter  │  │ DroneRouter   │ │    │
│  │  └──────────────┘  └──────────────┘  └───────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ WebSocket: order_tracking.py                     │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  Responsibility:                                        │    │
│  │  - Parse HTTP requests & validate (Pydantic)           │    │
│  │  - Handle WebSocket connections                        │    │
│  │  - Call use cases via FastAPI Depends()                │    │
│  │  - Return HTTP responses                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                             ↓                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │      APPLICATION LAYER (Business Logic/Use Cases)      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │    │
│  │  │ OrderUseCase │  │ PaymentUseCase│ │ AuthUseCase   │ │    │
│  │  └──────────────┘  └──────────────┘  └───────────────┘ │    │
│  │                                                         │    │
│  │  Responsibility:                                        │    │
│  │  - Execute business logic                              │    │
│  │  - Validate business rules                             │    │
│  │  - Orchestrate repositories & adapters                 │    │
│  │  - Return DTOs                                          │    │
│  │  - Raise custom exceptions                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                             ↓                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │        DATA LAYER (Repositories & Adapters)            │    │
│  │                                                         │    │
│  │  REPOSITORIES:          ADAPTERS:                       │    │
│  │  ┌────────────────┐    ┌──────────────────┐            │    │
│  │  │ OrderRepo      │    │ CloudinaryAdapter│            │    │
│  │  │ UserRepo       │    │ StripeAdapter    │            │    │
│  │  │ RestaurantRepo │    │ EmailAdapter     │            │    │
│  │  │ DroneRepo      │    └──────────────────┘            │    │
│  │  └────────────────┘                                     │    │
│  │                                                         │    │
│  │  Responsibility:                                        │    │
│  │  - Database CRUD operations (MongoDB queries)           │    │
│  │  - External API calls (Cloudinary, Stripe, etc.)        │    │
│  │  - Data serialization & deserialization                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                             ↓                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              CORE & SHARED MODULES                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │    │
│  │  │ Database │  │Exceptions│  │Constants │  │ Utils  │ │    │
│  │  │(MongoDB) │  │          │  │          │  │        │ │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │    │
│  └────────────────────────────────────────────────────────┘    │
│                             ↓                                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
        (HTTP Requests)        │        (Database Operations)
                               │        (API Calls)
                               ↓
        ┌──────────────────────────────────────────┐
        │      External Services & Databases       │
        │  ┌──────────────┐  ┌────────────────┐   │
        │  │  MongoDB     │  │  Cloudinary    │   │
        │  └──────────────┘  └────────────────┘   │
        │  ┌──────────────┐  ┌────────────────┐   │
        │  │  Stripe      │  │  Email Service │   │
        │  └──────────────┘  └────────────────┘   │
        └──────────────────────────────────────────┘
```

---

## 🔀 DATA FLOW: Creating an Order

### Complete Request/Response Cycle

```
1. CLIENT SENDS REQUEST
   ┌────────────────────────────────────────────────┐
   │ HTTP POST /api/orders                          │
   │ Content-Type: application/json                 │
   │                                                │
   │ {                                              │
   │   "customer_id": "cust_123",                   │
   │   "restaurant_id": "rest_456",                 │
   │   "items": [                                   │
   │     {                                          │
   │       "menu_item_id": "item_789",              │
   │       "quantity": 2,                           │
   │       "name": "Pizza",                         │
   │       "price": 12.99                           │
   │     }                                          │
   │   ],                                           │
   │   "total": 25.98,                              │
   │   "delivery_address": "123 Main St"            │
   │ }                                              │
   └────────────────────────────────────────────────┘
                          ↓
2. PRESENTATION LAYER (FastAPI Router)
   ┌────────────────────────────────────────────────┐
   │ @router.post("/orders")                        │
   │                                                │
   │ 1. Parse JSON body                             │
   │ 2. Validate with Pydantic (OrderCreateDTO)     │
   │    - Check required fields                     │
   │    - Validate data types                       │
   │    - Check constraints (min/max)               │
   │ 3. Call dependency: get_order_use_case()       │
   │ 4. Pass to use case                            │
   └────────────────────────────────────────────────┘
                          ↓
3. DEPENDENCY INJECTION (FastAPI Depends)
   ┌────────────────────────────────────────────────┐
   │ def get_order_use_case(                        │
   │     order_repo = Depends(get_order_repo),      │
   │     restaurant_repo = Depends(...),            │
   │     menu_repo = Depends(...),                  │
   │     ...                                        │
   │ ) -> OrderUseCase:                             │
   │     return OrderUseCase(                       │
   │         order_repo, restaurant_repo, ...      │
   │     )                                          │
   │                                                │
   │ FastAPI Creates:                               │
   │ - OrderRepository()                            │
   │ - RestaurantRepository()                       │
   │ - MenuRepository()                             │
   │ - OrderUseCase(all repos)                      │
   └────────────────────────────────────────────────┘
                          ↓
4. APPLICATION LAYER (Use Case - Business Logic)
   ┌────────────────────────────────────────────────┐
   │ async def create_order(self, ...)              │
   │                                                │
   │ # RULE 1: Validate restaurant exists           │
   │ restaurant = await                             │
   │   self.restaurant_repo.get_by_id(rest_456)    │
   │ if not restaurant:                             │
   │   raise ResourceNotFoundException(...)         │
   │ if not restaurant["is_active"]:                │
   │   raise BusinessRuleException(...)             │
   │                                                │
   │ # RULE 2: Validate items exist                 │
   │ for item in items:                             │
   │   menu_item = await                            │
   │     self.menu_repo.get_by_id(item["id"])      │
   │   if not menu_item:                            │
   │     raise ResourceNotFoundException(...)       │
   │                                                │
   │ # RULE 3: Validate total price                 │
   │ calculated_total = sum(price * qty...)         │
   │ if calculated_total != total:                  │
   │   raise BusinessRuleException(...)             │
   │                                                │
   │ # All rules passed - create order              │
   │ order_data = {...}                             │
   │ order = await self.order_repo.create(...)      │
   │                                                │
   │ return OrderResponseDTO(**order)               │
   └────────────────────────────────────────────────┘
                          ↓
5. DATA LAYER (Repositories - Database Operations)
   ┌────────────────────────────────────────────────┐
   │ class OrderRepository(BaseRepository):          │
   │                                                │
   │   async def create(self, data):                │
   │     db = get_db()  # Get MongoDB instance      │
   │     result = await db.orders.insert_one(data)  │
   │     inserted_id = result.inserted_id           │
   │     return await self.get_by_id(                │
   │       str(inserted_id)                         │
   │     )                                          │
   │                                                │
   │   async def get_by_id(self, id):               │
   │     order = await db.orders.find_one(...)      │
   │     return self._serialize(order)              │
   │                                                │
   │   def _serialize(self, doc):                   │
   │     out = dict(doc)                            │
   │     out["id"] = str(out.pop("_id"))            │
   │     return out                                 │
   └────────────────────────────────────────────────┘
                          ↓
6. EXTERNAL SERVICE (MongoDB)
   ┌────────────────────────────────────────────────┐
   │ MongoDB Atlas                                  │
   │                                                │
   │ db.orders.insert_one({                         │
   │   "_id": ObjectId("..."),                      │
   │   "customer_id": "cust_123",                   │
   │   "restaurant_id": "rest_456",                 │
   │   "items": [...],                              │
   │   "total": 25.98,                              │
   │   "status": "PENDING",                         │
   │   "created_at": "2024-01-14T...",              │
   │   "updated_at": "2024-01-14T..."               │
   │ })                                             │
   │                                                │
   │ Returns: {"_id": ObjectId("..."), ...}         │
   └────────────────────────────────────────────────┘
                          ↓
7. BUBBLE BACK UP (Response)
   ┌────────────────────────────────────────────────┐
   │ OrderRepository.get_by_id()                    │
   │ ↓ (returns serialized order)                   │
   │ {                                              │
   │   "id": "507f1f77bcf86cd799439011",            │
   │   "customer_id": "cust_123",                   │
   │   ...                                          │
   │ }                                              │
   │ ↓                                              │
   │ OrderUseCase.create_order()                    │
   │ ↓ (wraps in DTO)                               │
   │ OrderResponseDTO(**order)                      │
   │ ↓                                              │
   │ Router                                         │
   │ ↓ (caught return value)                        │
   │ return order_dto                               │
   │ ↓ (Pydantic serializes to JSON)                │
   │ FastAPI                                        │
   └────────────────────────────────────────────────┘
                          ↓
8. HTTP RESPONSE
   ┌────────────────────────────────────────────────┐
   │ HTTP 201 Created                               │
   │ Content-Type: application/json                 │
   │                                                │
   │ {                                              │
   │   "id": "507f1f77bcf86cd799439011",            │
   │   "customer_id": "cust_123",                   │
   │   "restaurant_id": "rest_456",                 │
   │   "items": [                                   │
   │     {                                          │
   │       "menu_item_id": "item_789",              │
   │       "quantity": 2,                           │
   │       "name": "Pizza",                         │
   │       "price": 12.99,                          │
   │       "subtotal": 25.98                        │
   │     }                                          │
   │   ],                                           │
   │   "total": 25.98,                              │
   │   "status": "PENDING",                         │
   │   "delivery_address": "123 Main St",           │
   │   "created_at": "2024-01-14T...",              │
   │   "updated_at": "2024-01-14T..."               │
   │ }                                              │
   └────────────────────────────────────────────────┘
                          ↓
9. CLIENT RECEIVES
   ┌────────────────────────────────────────────────┐
   │ React/JavaScript                               │
   │                                                │
   │ const response = await orderClient.createOrder({
   │   ...data                                      │
   │ })                                             │
   │                                                │
   │ console.log(response)                          │
   │ // {id: "507f1f...", status: "PENDING", ...}   │
   │                                                │
   │ setOrderId(response.id)                        │
   │ navigate(`/track/${response.id}`)              │
   └────────────────────────────────────────────────┘
```

---

## 🔄 ERROR HANDLING FLOW

```
SCENARIO: Client sends order with invalid total (price doesn't match)

CLIENT SENDS
│
├─ POST /api/orders
│ ├─ customer_id: "cust_123"
│ ├─ total: 100.00  ← WRONG! (items only cost $25.98)
│ └─ ...
│
PRESENTATION LAYER (Router)
│
├─ ✅ Pydantic validation passes (just checks types)
├─ Calls OrderUseCase.create_order()
│
APPLICATION LAYER (Use Case)
│
├─ Gets restaurants: ✅ OK
├─ Gets menu items: ✅ OK
├─ Calculates total: 25.98
├─ Compares with request: 100.00 != 25.98
├─ ❌ BUSINESS RULE VIOLATED!
├─ raise BusinessRuleException("Price mismatch")
│
PRESENTATION LAYER (Router - Exception Handler)
│
├─ except BusinessRuleException as e:
├─ raise HTTPException(status_code=422, detail=str(e))
│
FASTAPI
│
├─ Catches HTTPException
├─ Formats response
│
CLIENT RECEIVES
│
├─ HTTP 422 Unprocessable Entity
├─ {
│   "detail": "Price mismatch. Expected 25.98, got 100.00"
│ }
└─ UI shows error message to user
```

---

## 🗺️ DEPENDENCY GRAPH (What Depends on What)

```
NO BACKWARD DEPENDENCIES ALLOWED!

                  [Presentation]
                  /     |       \
                 /      |        \
            [Routers]  [Pages]  [Components]
                 \      |        /
                  \     |       /
                   ↓    ↓    ↓
              [Application]
              /           \
          [Use Cases]  [DTOs]
             /    \      /
            /      \    /
           ↓        ↓  ↓
          [Data Layer]
         /           \
    [Repos]       [Adapters]
        |             |
        ↓             ↓
    [DB]      [External APIs]


VALID DEPENDENCIES:
✅ Routers → Use Cases
✅ Use Cases → Repositories + Adapters
✅ Repositories → Database
✅ Adapters → External APIs

INVALID DEPENDENCIES:
❌ Database → Application
❌ Application → Routers
❌ Routers → Routers (circular)
❌ Repositories → Use Cases
❌ Adapters → Repositories
```

---

## 📊 LAYER INDEPENDENCE MATRIX

```
Can Presentation Layer code access...
├─ Its own code? ✅ YES (routers.py → routers.py)
├─ Application layer? ✅ YES (routers → use_cases)
├─ Data layer? ❌ NO (don't access DB directly)
└─ External services? ❌ NO (use adapters)

Can Application Layer code access...
├─ Its own code? ✅ YES (use_cases → use_cases)
├─ Presentation layer? ❌ NO (no HTTP context)
├─ Data layer? ✅ YES (use_cases → repos)
└─ External services? ✅ YES (via adapters)

Can Data Layer code access...
├─ Its own code? ✅ YES (repos → repos)
├─ Presentation layer? ❌ NO (don't know about routes)
├─ Application layer? ❌ NO (no business logic)
└─ External services? ✅ YES (direct API calls)
```

---

## 🎯 LAYER INTERACTION EXAMPLE: Restaurant Logo Upload

```
FRONTEND:
  Page: RestaurantDashboard.jsx
    ↓ (uploads file)
  Hook: useRestaurant.js
    ↓ (calls API client)
  Service: restaurant_client.js
    ↓ (POST /api/restaurants/{id}/logo)

BACKEND PRESENTATION LAYER:
  Router: restaurant_router.py
    @router.post("/restaurants/{id}/logo")
    async def upload_logo(id: str, file: UploadFile, use_case = Depends(...)):
        ↓ (calls use case)

BACKEND APPLICATION LAYER:
  Use Case: restaurant_use_case.py
    async def update_logo(restaurant_id, file):
        1. Validate restaurant exists
        2. Delete old logo (call adapter)
        3. Upload new logo (call adapter)
        4. Save URL to repository
        5. Return updated restaurant
        ↓ (uses repositories & adapters)

BACKEND DATA LAYER:
  Repository: restaurant_repository.py
    async def update(id, data):
        Save to MongoDB
  
  Adapter: cloudinary_adapter.py
    async def upload_image(file, folder):
        Call Cloudinary API
    async def delete_image(url):
        Call Cloudinary API

EXTERNAL:
  MongoDB: Save restaurant data
  Cloudinary: Store image files

RESPONSE FLOWS BACK UP:
  Cloudinary → Adapter → Use Case → Router → API Response → Frontend
```

---

## 🧪 TESTING PYRAMID

```
        ┌──────────────────┐
        │  API Tests (E2E) │  ← Test full request/response
        │   (10-20 tests)  │  ← Real server, real DB
        └──────────────────┘
                  ▲
                 / \
                /   \
       ┌──────────────────────┐
       │ Integration Tests    │  ← Test repositories with real DB
       │  (20-40 tests)       │  ← Mock use cases layer
       └──────────────────────┘
                    ▲
                   / \
                  /   \
       ┌──────────────────────────┐
       │  Unit Tests              │  ← Test business logic
       │  (100-200 tests)         │  ← Mock all dependencies
       └──────────────────────────┘

WHERE TO TEST EACH LAYER:

Presentation (Routers):
├─ API Tests (with real DB)
├─ Mock repositories
└─ Test HTTP status codes

Application (Use Cases):
├─ Unit Tests (with mock repos)
├─ No real DB needed
├─ Test business rules
└─ Test error handling

Data (Repositories):
├─ Integration Tests (with real DB)
├─ Test queries
├─ Test serialization
└─ API Tests (through full stack)
```

---

## 🔐 DEPENDENCY INJECTION FLOW

```
main.py
│
├─ FastAPI app initialization
├─ Include routers
│
┌─ Request comes in /api/orders
│
├─ Router: @router.post("/orders", use_case: OrderUseCase = Depends(get_order_use_case))
│
├─ FastAPI calls get_order_use_case() dependency
│   │
│   ├─ get_order_use_case() calls get_order_repo()
│   │   │
│   │   └─ Creates OrderRepository()
│   │       │
│   │       └─ Returns repository instance
│   │
│   ├─ get_order_use_case() calls get_restaurant_repo()
│   │   │
│   │   └─ Creates RestaurantRepository()
│   │
│   ├─ get_order_use_case() calls get_menu_repo()
│   │   │
│   │   └─ Creates MenuRepository()
│   │
│   └─ get_order_use_case() creates OrderUseCase(order_repo, restaurant_repo, menu_repo)
│       │
│       └─ Returns use case instance with all dependencies injected
│
├─ Router receives use case with all dependencies
│
├─ Router calls use_case.create_order(...)
│   │
│   ├─ Use case calls self.restaurant_repo.get_by_id(...)
│   ├─ Use case calls self.menu_repo.get_items(...)
│   ├─ Use case calls self.order_repo.create(...)
│   │
│   └─ Returns result
│
├─ Router returns HTTP response
│
└─ Response sent to client


KEY POINTS:
- Dependencies created fresh for each request (FastAPI caches within request)
- Change implementation in ONE PLACE (dependencies.py)
- All instances properly initialized
- No global state
- Easy to mock in tests
```

---

## 📈 SCALING PATTERNS

### Pattern 1: Caching Layer

```
Request
│
├─ Router
├─ Use Case
├─ Repository
├─ ❌ Not in cache → Query DB
├─ MongoDB → Returns data
├─ Cache layer stores result
│
NEXT REQUEST (same query):
│
├─ Router
├─ Use Case
├─ Repository
├─ ✅ Found in cache → Return immediately
└─ No DB query needed (FAST!)
```

### Pattern 2: Multiple Adapters

```
RestaurantUseCase needs to upload images

Option 1 (Tight):
├─ Direct CloudinaryAdapter call
├─ Hard to swap

Option 2 (Loose):
├─ IStorageAdapter interface
├─ CloudinaryAdapter implements it
├─ AwsS3Adapter implements it
├─ AzureBlobAdapter implements it
│
In dependencies.py:
├─ if USE_CLOUDINARY: StorageAdapter = CloudinaryAdapter()
├─ elif USE_AWS: StorageAdapter = AwsS3Adapter()
├─ else: StorageAdapter = AzureBlobAdapter()
│
All use cases work with ANY adapter!
```

### Pattern 3: Event-Driven

```
OrderUseCase.create_order():
├─ Create order in DB
├─ Emit OrderCreatedEvent
│   ├─ PaymentService listens → Charge customer
│   ├─ NotificationService listens → Send email
│   ├─ AnalyticsService listens → Track metric
│   └─ DroneService listens → Find nearest drone
│
Benefits:
├─ Services don't depend on each other
├─ Easy to add new listeners
├─ Scalable to microservices
```

---

## 🎨 SUMMARY VISUAL

```
┌─────────────────────────────────────────────────────────────────┐
│              3-TIER ARCHITECTURE VISUALIZATION                  │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   LAYER 1   │     │   LAYER 2   │     │   LAYER 3   │       │
│  │PRESENTATION │     │APPLICATION  │     │    DATA     │       │
│  ├─────────────┤     ├─────────────┤     ├─────────────┤       │
│  │ Routers     │────▶│ Use Cases   │────▶│Repositories│       │
│  │ WebSockets  │     │ Services    │     │ Adapters   │       │
│  │ Controllers │     │ Validators  │     │ DB Queries │       │
│  │             │     │ DTOs        │     │ API Calls  │       │
│  │ (HTTP Layer)│     │(Logic Layer)│     │(Data Layer)│       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│       ↓                    ↓                    ↓                │
│    Parse &             Execute              Persist &           │
│    Validate            Business             Retrieve            │
│    Requests            Logic                Data                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

KEY PRINCIPLES:
✓ Each layer has ONE responsibility
✓ Layers depend DOWNWARD only
✓ Easy to test (mock dependencies)
✓ Easy to change (swap implementations)
✓ Easy to scale (add features without touching others)
```

