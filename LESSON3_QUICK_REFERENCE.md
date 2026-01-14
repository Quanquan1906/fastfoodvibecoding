# Lesson 3: Quick Reference - 3-Tier Architecture Cheat Sheet

## 🏗️ ARCHITECTURE AT A GLANCE

```
┌─────────────────────────────────────────────────┐
│ PRESENTATION (Views & Controllers)              │
│ - HTTP Routers (@router.post("/api/..."))       │
│ - WebSocket handlers                            │
│ - React Components & Pages                      │
│ Responsibility: Parse request → Call service    │
└─────────────────────────────────────────────────┘
              ↓ (depends on)
┌─────────────────────────────────────────────────┐
│ APPLICATION (Business Logic & Use Cases)        │
│ - OrderUseCase, PaymentUseCase                  │
│ - Validation & business rules                   │
│ - Service orchestration                         │
│ Responsibility: Execute logic → Return result   │
└─────────────────────────────────────────────────┘
              ↓ (depends on)
┌─────────────────────────────────────────────────┐
│ DATA (Persistence & External APIs)              │
│ - Repositories (MongoDB queries)                │
│ - Adapters (Cloudinary, Stripe)                 │
│ Responsibility: CRUD operations only            │
└─────────────────────────────────────────────────┘
```

---

## 📁 FOLDER STRUCTURE QUICK COPY

### Backend Structure
```
backend/app/
├── presentation/
│   ├── routers/              ← API endpoints
│   │   ├── order_router.py
│   │   ├── auth_router.py
│   │   └── ...
│   ├── websocket/            ← WebSocket handlers
│   │   └── order_tracking.py
│   └── dependencies.py       ← FastAPI Depends()
│
├── application/
│   ├── use_cases/            ← Business logic
│   │   ├── order_use_case.py
│   │   └── ...
│   ├── dto/                  ← Data Transfer Objects
│   │   ├── order_dto.py
│   │   └── ...
│   └── interfaces/           ← Abstractions
│       ├── repository.py
│       └── storage_adapter.py
│
├── data/
│   ├── repositories/         ← Database queries
│   │   ├── base_repository.py
│   │   ├── order_repository.py
│   │   └── ...
│   ├── adapters/             ← External services
│   │   ├── cloudinary_adapter.py
│   │   └── payment_adapter.py
│   ├── database.py           ← DB connection
│   └── models/               ← Domain entities
│       ├── order.py
│       └── ...
│
└── shared/
    ├── exceptions.py         ← Custom errors
    ├── constants.py
    └── utils.py
```

### Frontend Structure
```
frontend/src/
├── presentation/
│   ├── pages/                ← Page components
│   │   ├── customer/
│   │   ├── restaurant/
│   │   └── admin/
│   ├── components/           ← Reusable components
│   │   ├── OrderCard.jsx
│   │   ├── DroneMap.jsx
│   │   └── ...
│   └── hooks/                ← Custom hooks (business logic)
│       ├── useOrder.js
│       └── useAuth.js
│
└── infrastructure/
    ├── api/                  ← API clients
    │   ├── client.js         ← Axios config
    │   ├── order_client.js
    │   └── ...
    ├── websocket/            ← WS connection
    └── context/              ← Global state
```

---

## 🔧 KEY FILES & WHAT GOES IN EACH

| File | Contains | Example |
|------|----------|---------|
| `*_router.py` | FastAPI endpoints | `@router.post("/orders")` |
| `*_use_case.py` | Business logic | `async def create_order(...)` |
| `*_repository.py` | DB queries | `async def create(data)` |
| `*_adapter.py` | External API calls | CloudinaryAdapter, StripeAdapter |
| `*_dto.py` | Request/response models | `class OrderCreateDTO(BaseModel)` |
| `interfaces.py` | Abstract classes | `class IRepository(ABC)` |
| `dependencies.py` | FastAPI Depends() | `def get_order_use_case()` |
| `exceptions.py` | Custom errors | `class BusinessRuleException` |

---

## 💡 LAYER RESPONSIBILITIES

### PRESENTATION LAYER (Routers, Pages, Components)

**What it DOES:**
- ✅ Parse HTTP requests
- ✅ Validate input with Pydantic
- ✅ Call use case/service
- ✅ Return HTTP response
- ✅ Render UI (frontend)

**What it DOES NOT:**
- ❌ Database queries
- ❌ Business logic
- ❌ External API calls

**Example:**
```python
@router.post("/orders")
async def create_order(request: OrderCreateDTO, use_case = Depends(...)):
    # Just call the use case
    return await use_case.create_order(...)
```

---

### APPLICATION LAYER (Use Cases, Services)

**What it DOES:**
- ✅ Execute business logic
- ✅ Validate business rules
- ✅ Orchestrate repositories
- ✅ Coordinate external services
- ✅ Return DTOs

**What it DOES NOT:**
- ❌ Access database directly (use repositories)
- ❌ Call external APIs directly (use adapters)
- ❌ Handle HTTP requests
- ❌ Render UI

**Example:**
```python
class OrderUseCase:
    async def create_order(self, data):
        # Business logic here
        restaurant = await self.restaurant_repo.get_by_id(...)
        if not restaurant.is_active:
            raise BusinessRuleException("Restaurant inactive")
        # More logic...
        return await self.order_repo.create(...)
```

---

### DATA LAYER (Repositories, Adapters)

**What it DOES:**
- ✅ Database CRUD operations
- ✅ External API calls
- ✅ Data serialization

**What it DOES NOT:**
- ❌ Business logic
- ❌ Validation (beyond schema)
- ❌ HTTP concerns

**Example:**
```python
class OrderRepository:
    async def create(self, data):
        db = get_db()
        result = await db.orders.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))
```

---

## 🧬 DEPENDENCY FLOW

```python
# 1. HTTP Request comes in
POST /api/orders
{
    "customer_id": "c1",
    "restaurant_id": "r1",
    "items": [...],
    "total": 25.99,
    "delivery_address": "123 Main"
}

# 2. Router receives and validates
@router.post("/orders")
async def create_order(request: OrderCreateDTO, use_case = Depends(get_order_use_case)):
    # request is validated by Pydantic automatically

# 3. FastAPI calls get_order_use_case() dependency
def get_order_use_case(
    order_repo = Depends(get_order_repo),
    restaurant_repo = Depends(get_restaurant_repo)
):
    return OrderUseCase(order_repo, restaurant_repo)

# 4. Creates OrderUseCase with injected repositories
# 5. Router calls use_case.create_order()
# 6. Use case calls repositories:
#    - restaurant_repo.get_by_id()
#    - menu_repo.validate_items()
#    - order_repo.create()
# 7. Repositories execute database operations
# 8. Results bubble back up
# 9. Router formats response and returns JSON
```

---

## 📝 COMMON PATTERNS

### Pattern 1: Creating Repositories

```python
# 1. Define interface (Data layer)
class IOrderRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict) -> Dict:
        pass

# 2. Implement repository
class OrderRepository(IOrderRepository):
    async def create(self, data: Dict) -> Dict:
        db = get_db()
        result = await db.orders.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

# 3. Inject into use case
class OrderUseCase:
    def __init__(self, repo: IOrderRepository):
        self.repo = repo
    
    async def create_order(self, data):
        return await self.repo.create(data)
```

### Pattern 2: Creating Adapters

```python
# 1. Define interface
class IStorageAdapter(ABC):
    @abstractmethod
    async def upload_image(self, file, filename, folder) -> str:
        pass

# 2. Implement adapter
class CloudinaryAdapter(IStorageAdapter):
    async def upload_image(self, file, filename, folder):
        # Call Cloudinary API
        return url

# 3. Use in use case
class RestaurantUseCase:
    def __init__(self, storage: IStorageAdapter):
        self.storage = storage
    
    async def update_logo(self, file):
        url = await self.storage.upload_image(file, ...)
        # ...

# 4. Easy to swap
# In dependencies.py:
def get_storage_adapter():
    return CloudinaryAdapter()  # or S3Adapter(), AzureAdapter()
```

### Pattern 3: Dependency Injection in FastAPI

```python
# Repository dependency
def get_order_repo() -> OrderRepository:
    return OrderRepository()

# Use case dependency (depends on repo)
def get_order_use_case(
    repo: OrderRepository = Depends(get_order_repo)
) -> OrderUseCase:
    return OrderUseCase(repo)

# In router
@router.post("/orders")
async def create_order(
    data: OrderCreateDTO,
    use_case: OrderUseCase = Depends(get_order_use_case)
):
    return await use_case.create_order(...)
```

### Pattern 4: Error Handling

```python
# In use case (raise meaningful exceptions)
async def create_order(self, data):
    restaurant = await self.repo.get_by_id(data["restaurant_id"])
    if not restaurant:
        raise ResourceNotFoundException("Restaurant not found")
    
    if not restaurant["is_active"]:
        raise BusinessRuleException("Restaurant not accepting orders")

# In router (catch and convert to HTTP errors)
@router.post("/orders")
async def create_order(data, use_case = Depends(...)):
    try:
        return await use_case.create_order(data)
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## ✅ BEST PRACTICES

### ✅ DO:
- Use **dependency injection** everywhere
- Keep **business logic in use cases**
- **Abstract external services** with adapters
- **Test business logic** with mock repositories
- Use **type hints** for clarity
- Raise **custom exceptions** with clear messages
- Return **DTOs** from use cases
- Keep **routers simple** (10 lines max per endpoint)

### ❌ DON'T:
- Call database from routers directly
- Access HTTP context from use cases
- Put business logic in repositories
- Import presentation layer in data layer
- Use `get_db()` outside repositories
- Raise `HTTPException` in use cases
- Store state in use case instances
- Create circular dependencies between layers

---

## 🧪 TESTING PATTERNS

### Unit Test (No DB)

```python
@pytest.mark.asyncio
async def test_order_creation():
    # Inject mock repositories
    repo = MockOrderRepository()
    use_case = OrderUseCase(repo)
    
    # Test business logic
    result = await use_case.create_order(
        customer_id="c1",
        restaurant_id="r1",
        items=[...],
        total=25.99,
        address="123 Main"
    )
    
    assert result.status == "PENDING"
    assert repo.created_count == 1
```

### Integration Test (Real DB)

```python
@pytest.mark.asyncio
async def test_order_repository():
    repo = OrderRepository()  # Real repository
    
    # Connect to test MongoDB
    await connect_test_db()
    
    result = await repo.create({...})
    assert result["id"]
    
    await close_test_db()
```

### API Test

```python
@pytest.mark.asyncio
async def test_create_order_endpoint(client):
    response = client.post("/api/orders", json={
        "customer_id": "c1",
        "restaurant_id": "r1",
        "items": [...],
        "total": 25.99,
        "delivery_address": "123 Main"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
```

---

## 🔍 DEBUGGING TIPS

**If business logic is broken:**
- Look in `*_use_case.py` for the logic
- Check exception messages - they should tell you which rule failed

**If database is returning wrong data:**
- Check `*_repository.py` for the query
- Add print statements or breakpoints in repository

**If API endpoint not working:**
- Check `*_router.py` for the route definition
- Check error handling catches the right exceptions

**If external service (Cloudinary) not working:**
- Check `*_adapter.py` for the implementation
- Check environment variables are set

---

## 📊 QUICK MIGRATION CHECKLIST

For each domain (Order, Payment, Auth, etc.):

```
□ Create OrderRepository(BaseRepository)
  - Move all db.orders queries here
  
□ Create OrderUseCase
  - Move all business logic here
  - Inject OrderRepository
  
□ Create OrderRouter
  - Move all /orders/* endpoints here
  - Call OrderUseCase via Depends()
  
□ Create OrderDTO(s)
  - Request models
  - Response models
  
□ Update main.py
  - Import and include OrderRouter
  
□ Test all endpoints
  - POST /orders (create)
  - GET /orders/{id} (get)
  - GET /orders (list)
  - PATCH /orders/{id}/status (update)
  
□ Delete old code
  - Remove from old routes.py
  - Remove old service
```

---

## 🎯 MIGRATION TIMELINE

| Phase | Time | Tasks |
|-------|------|-------|
| **1** | 1-2h | Create folder structure + exceptions |
| **2** | 2-3h | Create base interfaces (Repository, Adapter) |
| **3** | 3-4h | Refactor **Orders** domain completely |
| **4** | 2-3h | Refactor **Auth** domain |
| **5** | 2-3h | Refactor **Restaurant** domain |
| **6** | 2-3h | Refactor **Menu** domain |
| **7** | 2-3h | Refactor **Drone** domain |
| **8** | 2-3h | Refactor **Payment** domain |
| **9** | 2-3h | Frontend refactoring (services + hooks) |
| **10** | 1-2h | Testing & cleanup |
| **TOTAL** | **~25-30 hours** | Full refactoring |

---

## 💻 CODE SNIPPETS FOR COPY-PASTE

### Snippet 1: Base Repository

```python
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict

class BaseRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
```

### Snippet 2: Use Case Template

```python
class OrderUseCase:
    def __init__(self, order_repo, restaurant_repo, menu_repo):
        self.order_repo = order_repo
        self.restaurant_repo = restaurant_repo
        self.menu_repo = menu_repo
    
    async def create_order(self, customer_id, restaurant_id, items, total, address):
        # Validate inputs
        if not customer_id:
            raise ValidationException("customer_id required")
        
        # Validate business rules
        restaurant = await self.restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise ResourceNotFoundException("Restaurant not found")
        
        # Execute
        order = await self.order_repo.create({
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            # ...
        })
        
        return order
```

### Snippet 3: Router Template

```python
@router.post("/orders", response_model=OrderResponseDTO)
async def create_order(
    request: OrderCreateDTO,
    use_case: OrderUseCase = Depends(get_order_use_case)
):
    try:
        return await use_case.create_order(
            customer_id=request.customer_id,
            restaurant_id=request.restaurant_id,
            items=request.items,
            total=request.total,
            address=request.address
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 🎓 KEY TAKEAWAYS

1. **Layers are dependencies**: Presentation depends on Application, Application on Data
2. **Never cross layers backwards**: Data layer should NOT import from Presentation
3. **Abstract external services**: Use adapters for Cloudinary, Stripe, etc.
4. **Inject dependencies**: Use FastAPI `Depends()` to inject repositories
5. **DTOs decouple layers**: Use DTOs between layers to prevent tight coupling
6. **Business logic goes in use cases**: Services are the heart of the app
7. **Repositories hide databases**: No one talks to DB except repositories
8. **Tests mock repositories**: Unit tests use mock repos, no real DB needed

---

## 📚 REFERENCE LINKS IN THIS PROJECT

- Full guide: `LESSON3_ARCHITECTURE_REFACTOR.md`
- Code examples: `LESSON3_REFACTORED_CODE_EXAMPLES.md`
- Implementation: `LESSON3_BENEFITS_AND_IMPLEMENTATION.md`

