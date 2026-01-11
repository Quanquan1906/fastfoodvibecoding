# Business Requirements Document (BRD)
## FastFood Delivery Demo System

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Current Implementation

---

## 1. Business Overview

### 1.1 System Purpose
The FastFood Delivery System is a demonstration platform designed to showcase a multi-tenant food delivery service powered by autonomous drone technology. The platform enables restaurants to manage their menus, process customer orders, and track deliveries in real-time.

### 1.2 Key Innovation
Autonomous drone delivery: A drone-based delivery system that provides real-time tracking from restaurant to customer location, reducing delivery time and operational costs.

### 1.3 Target Market
- **Restaurant Owners:** Independent food establishments seeking modern order management
- **Customers:** Urban food delivery consumers wanting quick, tracked deliveries
- **System Administrators:** Manage the platform infrastructure, restaurants, and drones

### 1.4 Deployment Model
- Multi-tenant SaaS platform
- Demonstration system (not production)
- Docker containerized deployment
- Responsive web interface (React frontend)
- RESTful API backend (FastAPI)
- MongoDB document database

---

## 2. Business Objectives

### 2.1 Primary Objectives
1. **Enable Restaurant Digital Transformation**
   - Provide restaurants with modern online ordering capabilities
   - Streamline menu management and order processing
   - Enable real-time order status tracking

2. **Improve Delivery Experience**
   - Reduce delivery time through drone automation
   - Provide real-time tracking of deliveries
   - Display delivery address and estimated arrival

3. **Establish Multi-Tenant Model**
   - Support multiple restaurants on a single platform
   - Enforce restaurant ownership and isolation
   - Enable centralized administration

4. **Demonstrate Scalability**
   - Support growing restaurant and customer base
   - Handle pagination for browsing restaurants
   - Manage order lifecycle across multiple restaurants

### 2.2 Secondary Objectives
- Implement role-based access control
- Provide payment processing (mock demonstration)
- Enable drone fleet management per restaurant
- Support real-time WebSocket updates for order tracking

---

## 3. Stakeholders

| Stakeholder | Role | Interests |
|---|---|---|
| **Restaurant Owner** | Food business operator | Menu management, order processing, delivery tracking, revenue |
| **Customer** | End user | Easy ordering, transparent pricing, real-time delivery tracking, address privacy |
| **System Administrator** | Platform operator | Platform stability, user management, restaurant provisioning, drone fleet oversight |
| **Delivery Drone** | Automated delivery system | Route optimization, status reporting, real-time location tracking |
| **Tech Support** | Operational support | Monitoring, debugging, user assistance |

---

## 4. User Roles & Permissions Matrix

### 4.1 ADMIN (System Administrator)

**Responsibilities:**
- Manage all restaurants on the platform
- Create and configure restaurants with owner assignments
- Manage drone fleet across all restaurants
- View all orders system-wide
- Access all system analytics and reports

**Permissions:**
| Action | Permission |
|---|---|
| View all restaurants | ✓ Allowed |
| Create restaurant | ✓ Allowed |
| Edit any restaurant | ✓ Allowed |
| Delete restaurant | ✓ Allowed |
| Manage all drones | ✓ Allowed |
| View all orders | ✓ Allowed |
| View all users | ✓ Allowed |
| Access admin dashboard | ✓ Allowed |

**Key Features:**
- Admin Dashboard with restaurant, drone, user, and order management
- Bulk restaurant creation with owner assignment
- Drone provisioning and assignment
- System-wide analytics and monitoring

---

### 4.2 RESTAURANT (Restaurant Owner/Manager)

**Responsibilities:**
- Manage restaurant menu items
- Process and accept/reject customer orders
- Assign drones to accepted orders
- Track order fulfillment
- Monitor delivery status

**Permissions:**
| Action | Permission |
|---|---|
| View own restaurant | ✓ Allowed |
| View other restaurants | ✗ Denied |
| Edit own restaurant | ✓ Allowed (via admin) |
| Create menu items | ✓ Allowed (for own restaurant) |
| Edit menu items | ✓ Allowed (for own restaurant) |
| Delete menu items | ✓ Allowed (for own restaurant) |
| View own orders | ✓ Allowed |
| View other restaurant orders | ✗ Denied |
| Accept/reject orders | ✓ Allowed (for own orders) |
| Update order status | ✓ Allowed (for own orders) |
| Assign drones | ✓ Allowed (to own orders) |
| View assigned drones | ✓ Allowed (own drones) |

**Key Features:**
- Restaurant Dashboard for order management
- Menu management interface with image uploads
- Order acceptance/rejection workflow
- Drone assignment for accepted orders
- Real-time order status updates via WebSocket
- Order history and filtering

**Access Control Rule:**
```
Restaurant user can ONLY access restaurant where:
  restaurant.ownerUsername === loggedInUser.username
```
If condition not met → 403 Forbidden error

---

### 4.3 CUSTOMER (End User/Food Buyer)

**Responsibilities:**
- Browse available restaurants
- Browse restaurant menus
- Place food orders
- Make payment for orders
- Track deliveries in real-time
- View order history

**Permissions:**
| Action | Permission |
|---|---|
| Browse restaurants (paginated) | ✓ Allowed (no login required) |
| View restaurant details | ✓ Allowed (no login required) |
| View restaurant menu | ✓ Allowed (no login required) |
| Add items to cart | ✓ Required login |
| Place order | ✓ Allowed |
| Make payment | ✓ Allowed |
| Track order | ✓ Allowed |
| View order history | ✓ Allowed (own orders) |
| View other customer orders | ✗ Denied |

**Key Features:**
- Browse restaurants with pagination (6 per page)
- View menu items with prices and images
- Add to cart with quantity selection
- Enter delivery address at checkout
- View real-time delivery tracking
- Mock payment processing
- Order history access
- Real-time order status updates

**Authentication:**
- Username-only login (no password required in demo)
- Session stored in localStorage
- Automatic role assignment (CUSTOMER)

---

## 5. Business Processes

### 5.1 User Authentication

**Process Flow:**
1. User navigates to login page
2. Enters username
3. Selects role (Admin/Restaurant/Customer)
4. System authenticates and stores session
5. User redirected to role-specific dashboard

**Current State:** Demo-only (no password required)

**Data Stored in Session:**
```json
{
  "username": "john_pizza",
  "role": "RESTAURANT"
}
```

---

### 5.2 Restaurant Creation (Admin Function)

**Process Flow:**
```
Admin Dashboard
  ↓
Enter Restaurant Details:
  - Restaurant Name
  - Owner ID (system ID)
  - Owner Username (for ownership validation)
  - Description
  - Address
  - Phone
  - Image Upload (Cloudinary)
  ↓
System Validates Input
  ↓
Create Restaurant Document
  ↓
Link to Owner User Account
  ↓
Restaurant Active & Ready
```

**Business Rules:**
- Owner username is **immutable** after creation (cannot be changed)
- One restaurant per owner_id
- Image upload is mandatory (Cloudinary)
- Restaurant information is public (visible to all customers)

**Data Captured:**
- Restaurant name, address, phone
- Owner identification (ID and username)
- Description and branding (image)
- Created timestamp
- Pagination support (6 restaurants per page)

---

### 5.3 Menu Management (Restaurant Owner Function)

**Process Flow:**
```
Restaurant Dashboard → Menu Tab
  ↓
Add Menu Item:
  - Item Name
  - Description
  - Price
  - Image Upload (Cloudinary)
  - Availability Status
  ↓
System Validates
  ↓
Menu Item Created & Published
  ↓
Edit/Delete Existing Items
  ↓
Menu Live for Customers
```

**Business Rules:**
- Menu items are restaurant-specific (isolated)
- Prices must be non-negative currency values
- Images are optional but recommended
- Items can be marked as unavailable
- Quantity validation (minimum 1 item in cart)

**Capabilities:**
- Add new menu items
- Edit existing item details
- Delete items from menu
- Toggle item availability
- Image management via Cloudinary

---

### 5.4 Customer Browsing & Discovery

**Process Flow:**
```
Customer Home Page
  ↓
Browse Restaurants (Paginated)
  - Default: 6 restaurants per page
  - Next/Previous pagination controls
  - Restaurant cards with images & info
  ↓
Click "View Menu"
  ↓
Restaurant Detail + Menu Display
  - All menu items with prices
  - Item images
  - Descriptions
  ↓
Guest Browsing (No Login Required)
  - Can view restaurants
  - Can view menus
  - CANNOT add to cart or checkout
  ↓
Login Prompt on "Add to Cart"
  - Customer redirected to login
  - Returns to menu after login
```

**Business Rules:**
- Guests can browse without login
- Login required for cart actions
- No payment without login
- Delivery address required at checkout
- Real-time restaurant availability

---

### 5.5 Order Placement & Checkout

**Process Flow:**
```
Customer Cart → Checkout
  ↓
Verify Login
  ↓
Cart Contains:
  - Menu items with quantities
  - Item prices
  - Calculated total
  ↓
Enter Delivery Address
  - Street address
  - City/location
  - Delivery details
  ↓
Order Review:
  - Items (quantity × price)
  - Subtotal
  - Delivery address confirmation
  ↓
Place Order
  ↓
Order Created (Status: PENDING)
  ↓
Restaurant Notification
  ↓
Redirect to Order Tracking
```

**Business Rules:**
- Cart must contain minimum 1 item
- Delivery address is mandatory
- Total calculated as sum of (price × quantity)
- Order timestamp recorded
- Customer ID linked to order

**Order Data Captured:**
- Customer ID
- Restaurant ID
- Menu items (with prices and quantities)
- Total price
- Delivery address
- Order timestamp
- Order status (initial: PENDING)

---

### 5.6 Payment Processing (Mock Demonstration)

**Process Flow:**
```
Order Tracking Page
  ↓
Order Status: PENDING
  ↓
"Mock Payment" Button Available
  ↓
Customer Clicks Payment
  ↓
System Processes Mock Payment
  ↓
Order Status Updates to PREPARING
  ↓
Restaurant Notification
```

**Business Rules:**
- Payment is simulated (no real transactions)
- Always succeeds (for demo purposes)
- Triggers order status change
- Restaurant receives notification
- Demo message: "Mock Payment (Always Succeeds)"

**Note:** Production system would require:
- PCI DSS compliance
- Real payment gateway integration
- Fraud detection
- Receipt generation

---

### 5.7 Restaurant Order Management

**Process Flow:**
```
Restaurant Dashboard → Orders Tab
  ↓
View Pending Orders
  - Order ID
  - Customer details
  - Items ordered
  - Total price
  ↓
Accept or Reject Order
  ↓
If Accepted:
  Order Status: PREPARING
  ↓
Add Menu Items to Order
  ↓
Mark as Ready for Pickup
  Order Status: READY_FOR_PICKUP
  ↓
Select & Assign Drone
  - Available drones list
  - Automatic drone assignment
  ↓
Prepare for Delivery
  Order Status: DELIVERING
  ↓
Monitor Delivery Progress
  ↓
Complete Delivery
  Order Status: COMPLETED
```

**Order Status Lifecycle:**
```
PENDING
  ↓ (Payment received / Restaurant accepts)
PREPARING
  ↓ (Restaurant prepares order)
READY_FOR_PICKUP
  ↓ (Drone assigned)
DELIVERING
  ↓ (In transit to customer)
COMPLETED
  ↓ (Delivered to customer)
```

**Business Rules:**
- Restaurant must accept order before status changes
- Rejection removes order from queue
- Drone assignment mandatory for delivery
- Status updates notify customer in real-time
- Real-time WebSocket updates for tracking

---

### 5.8 Drone Delivery & Tracking

**Process Flow:**
```
Order Status: READY_FOR_PICKUP
  ↓
Restaurant Assigns Drone
  - Select from available drones
  - Drone status: AVAILABLE → BUSY
  ↓
Drone Notified
  ↓
Real-Time Tracking Begins
  - Drone location updated
  - Progress shown to customer (%)
  - Interactive map display
  - Estimated arrival time
  ↓
Drone Arrives at Customer
  ↓
Order Status: COMPLETED
  ↓
Drone Status: AVAILABLE (ready for next delivery)
```

**Drone Information Tracked:**
- Drone name/ID
- Current status (Available/Busy/Offline)
- Current latitude/longitude
- Restaurant assignment
- Delivery destination coordinates
- Real-time movement simulation

**Customer Visibility:**
- Drone position on map
- Delivery progress percentage
- Destination address confirmation
- Real-time updates via WebSocket
- Estimated delivery time

---

### 5.9 Order Tracking (Customer Function)

**Process Flow:**
```
Customer Order Confirmation
  ↓
Redirected to Tracking Page
  ↓
Display Order Details:
  - Order ID
  - Status badge with emoji
  - Items ordered (quantity × name)
  - Total price
  - Delivery address
  ↓
Order Status: PENDING
  - "Mock Payment" button available
  ↓
Payment Made
  ↓
Order Status: PREPARING
  - Message: "Restaurant is preparing your order"
  ↓
Order Status: READY_FOR_PICKUP
  - Drone awaiting pickup
  ↓
Order Status: DELIVERING
  - Interactive map with drone position
  - Progress bar (0-100%)
  - Real-time location updates
  - Delivery destination coordinates
  ↓
Order Status: COMPLETED
  - "Order delivered successfully" message
  - Full delivery map visible
  ↓
Return to Home
```

**Real-Time Features:**
- WebSocket connection for live updates
- Simulated drone movement (5% progress per second)
- Automatic order completion at 100% progress
- Live status emoji indicators
- Color-coded status badges

---

## 6. Access Control Rules

### 6.1 Authentication Model
- **Type:** Simple role-based (no password)
- **Session Storage:** Browser localStorage
- **Session Format:**
  ```json
  {
    "username": "user_identifier",
    "role": "ADMIN|RESTAURANT|CUSTOMER"
  }
  ```

### 6.2 Authorization Rules

#### Admin Access
```
Can access: ✓ Admin Dashboard
Cannot access: ✗ Customer/Restaurant dashboards (not needed)
All restaurant operations: ✓ Full visibility
All user operations: ✓ Full visibility
```

#### Restaurant Owner Access
```
Can access: ✓ Restaurant Dashboard (own restaurant only)
Cannot access: ✗ Other restaurants' dashboards
  
Ownership Validation:
  IF user.role == "RESTAURANT" 
    AND restaurant.ownerUsername == user.username
    THEN Allow access
  ELSE Deny with 403 Forbidden

Case handling: Case-insensitive, trimmed comparison
  example: "John_Pizza" == "john_pizza" ✓ (allowed)
```

#### Customer Access
```
Can access: ✓ Public pages (no login needed)
            ✓ Customer checkout
            ✓ Order tracking (own orders only)
Cannot access: ✗ Admin/Restaurant dashboards
            ✗ Other customers' order history

Order Access Validation:
  IF order.customer_id == logged_in_customer_id
    THEN Allow view
  ELSE Deny access
```

### 6.3 Route Protection
| Route | Public | Login Required | Role Required |
|---|---|---|---|
| `/` (Home) | ✓ Yes | No | Any |
| `/login` | ✓ Yes | No | Any |
| `/customer/checkout/:id` | ✗ No | Yes | CUSTOMER |
| `/customer/track/:id` | ✗ No | Yes | CUSTOMER |
| `/customer/orders` | ✗ No | Yes | CUSTOMER |
| `/restaurant/dashboard` | ✗ No | Yes | RESTAURANT |
| `/admin/dashboard` | ✗ No | Yes | ADMIN |

---

## 7. Business Rules

### 7.1 Ownership Validation Rules

**Rule 1: Restaurant Ownership**
```
When: Restaurant user accesses restaurant
Validation: restaurant.ownerUsername == loggedInUser.username
Comparison: Case-insensitive, whitespace-trimmed
Result: 
  ✓ Match → Allow access
  ✗ Mismatch → 403 Forbidden, redirect to home
```

**Rule 2: Menu Item Isolation**
```
When: Restaurant manages menu items
Isolation: Menu items only visible/editable to owner
  - Items are filtered by restaurant_id
  - Only owner can add/edit/delete
  - Customers see all available items
```

**Rule 3: Order Isolation**
```
When: Users access orders
Isolation:
  - Customer: Can only view own orders (customer_id match)
  - Restaurant: Can only view orders for own restaurant
  - Admin: Can view all orders
```

### 7.2 Order Lifecycle Rules

**Rule 4: Order Status Transitions**
```
Valid Status Flow:
  PENDING → PREPARING → READY_FOR_PICKUP → DELIVERING → COMPLETED

Invalid Transitions:
  ✗ Cannot skip states (e.g., PENDING → DELIVERING)
  ✗ Cannot go backwards (e.g., DELIVERING → PREPARING)
  ✗ Cannot change completed orders
```

**Rule 5: Payment Requirement**
```
When: Order transitions from PENDING to PREPARING
Requirement: Payment must be processed
Current: Mock payment always succeeds
  - No validation needed
  - Message: "Mock Payment (Always Succeeds)"
```

**Rule 6: Drone Assignment Requirement**
```
When: Order status changes to DELIVERING
Requirement: Must have assigned drone
Validation:
  IF order.drone_id exists
    THEN allow DELIVERING status
  ELSE block transition
```

### 7.3 Data Validation Rules

**Rule 7: Order Data**
```
Cart Validation:
  - Minimum items: 1
  - Prices: Non-negative
  - Quantities: ≥ 1
  - Total: Sum of (price × quantity)

Delivery Address:
  - Required: Yes
  - Minimum length: 1 character
  - Maximum: 255 characters
```

**Rule 8: Menu Item Data**
```
Item Validation:
  - Name: Required, non-empty
  - Price: Required, ≥ 0
  - Description: Optional
  - Image: Optional (Cloudinary URL)
  - Available: Boolean (default: true)
```

**Rule 9: Restaurant Data**
```
Restaurant Validation:
  - Name: Required, unique per system
  - Owner ID: Required, system-assigned
  - Owner Username: Required, immutable
  - Address: Required for delivery
  - Phone: Contact information
  - Image: Required for display
```

### 7.4 Pagination Rules

**Rule 10: Restaurant Pagination**
```
Default Behavior:
  - Items per page: 6 restaurants
  - Sort order: Creation date (descending)
  - Navigation: Previous/Next buttons
  
Disabled on:
  - First page: "Previous" button disabled
  - Last page: "Next" button disabled
  - Single page: Both buttons hidden
```

---

## 8. Non-Functional Requirements

### 8.1 Performance Requirements

| Requirement | Target |
|---|---|
| Page load time (avg) | < 2 seconds |
| API response time (avg) | < 500 ms |
| Restaurant list query | < 1 second (paginated) |
| Real-time updates latency | < 1 second (WebSocket) |
| Concurrent users supported | 100+ |

### 8.2 Availability & Reliability

| Requirement | Target |
|---|---|
| System uptime | 99% (demo) |
| Data persistence | MongoDB with backups |
| Session persistence | Across browser refresh |
| Recovery time (RTO) | < 5 minutes |
| Recovery point (RPO) | < 1 hour |

### 8.3 Security Requirements

| Requirement | Implementation |
|---|---|
| User authentication | Simple role-based (demo) |
| Authorization | Access control checks per role |
| Data encryption | HTTPS recommended |
| Image storage | Cloudinary (external CDN) |
| CORS protection | API endpoint validation |
| API rate limiting | Not implemented (demo) |
| Input validation | Pydantic models (backend) |

### 8.4 Scalability Requirements

| Requirement | Target |
|---|---|
| Restaurants supported | 1000+ |
| Orders per day | 10,000+ |
| Concurrent connections | 500+ |
| Database indexes | Optimized for queries |
| Image storage | Cloudinary scalable CDN |
| Horizontal scaling | Docker containerized |

### 8.5 Usability Requirements

| Requirement | Implementation |
|---|---|
| Mobile responsive | CSS Grid/Flexbox |
| Accessibility | Semantic HTML, ARIA labels |
| Navigation clarity | Breadcrumbs, back buttons |
| Error messages | User-friendly alerts |
| Loading states | Spinners, disabled buttons |
| Real-time feedback | Status emojis, color badges |

### 8.6 Browser Compatibility

| Browser | Version |
|---|---|
| Chrome | Latest |
| Firefox | Latest |
| Safari | Latest |
| Edge | Latest |

### 8.7 Device Support

- Desktop: ✓ Fully supported
- Tablet: ✓ Responsive design
- Mobile: ✓ Touch-optimized

---

## 9. System Architecture Overview

### 9.1 Technology Stack

**Frontend:**
- React 19.2.3
- React Router v6
- Axios (HTTP client)
- Leaflet (Maps/Tracking)
- CSS3 (Responsive design)

**Backend:**
- FastAPI 0.104.1
- Python 3.11
- Uvicorn (ASGI server)
- Motor 3.3.2 (Async MongoDB)
- Pydantic (Data validation)

**Database:**
- MongoDB 7.0
- Document-oriented storage
- No SQL required

**External Services:**
- Cloudinary (Image/Media storage)
- Docker (Containerization)
- Docker Compose (Orchestration)

### 9.2 Deployment Architecture

```
Docker Compose Stack:
├── Frontend (React)
│   ├── Port: 3000
│   ├── Served via Node.js serve
│   └── Environment: REACT_APP_API_BASE_URL
├── Backend (FastAPI)
│   ├── Port: 8000
│   ├── Framework: FastAPI + Uvicorn
│   └── Database: MongoDB connection
└── Database (MongoDB)
    ├── Port: 27017
    ├── Data volume: mongodb_data
    └── Network: fastfood-network
```

### 9.3 API Structure

**Base URL:** `http://localhost:8000`

**Key Endpoints:**
- Authentication: `/login`
- Restaurants: `/restaurants`, `/restaurants/{id}`
- Orders: `/orders`, `/orders/{id}`
- Menus: `/restaurants/{id}/menu`, `/restaurant/menu`
- Payments: `/payments/mock/{order_id}`
- WebSocket: `/ws/orders/{order_id}` (tracking)

---

## 10. Out of Scope

### 10.1 Not Included in Current System

| Feature | Reason |
|---|---|
| Real payment gateway | Demo only (mock payment) |
| Password authentication | Demo uses username-only login |
| Email notifications | Not implemented |
| SMS notifications | Not implemented |
| Push notifications | Not implemented |
| AI-based recommendations | Out of scope |
| Advanced analytics | Basic dashboards only |
| Multi-language support | English only |
| Accessibility compliance (WCAG) | Partial support |
| Production security hardening | Demo implementation |
| Load balancing | Single instance |
| Database replication | No failover |
| API rate limiting | Not implemented |
| Request logging | Basic logging only |

### 10.2 Future Enhancement Opportunities

1. **Payment Integration**
   - Stripe/PayPal integration
   - PCI compliance
   - Invoice generation

2. **Notifications**
   - Email order confirmation
   - SMS delivery alerts
   - Push notifications

3. **Analytics**
   - Restaurant performance metrics
   - Customer behavior analysis
   - Revenue reporting

4. **Advanced Features**
   - Multiple delivery addresses per customer
   - Saved favorite restaurants
   - Rating and reviews system
   - Loyalty programs
   - Promotional discounts

5. **Operational Features**
   - Bulk restaurant import
   - Customer feedback management
   - Dispute resolution system
   - Driver insurance management

6. **Drone Management**
   - Battery management
   - Maintenance scheduling
   - Weather-based restrictions
   - No-fly zone management

---

## 11. Success Metrics (Demo Purpose)

### 11.1 Functional Success
- ✓ All user roles work independently
- ✓ Ownership validation prevents unauthorized access
- ✓ Orders complete full lifecycle (PENDING → COMPLETED)
- ✓ Real-time tracking displays correctly
- ✓ Payment processing (mock) succeeds
- ✓ Pagination works smoothly
- ✓ Menu management functional
- ✓ Drone assignment operational

### 11.2 System Success
- ✓ Docker deployment successful
- ✓ MongoDB persistence functional
- ✓ API response times acceptable
- ✓ Frontend renders without errors
- ✓ WebSocket real-time updates work
- ✓ Image uploads via Cloudinary functional
- ✓ Cross-origin requests work (CORS)

### 11.3 Business Success
- ✓ Multi-tenant isolation working
- ✓ Role-based access enforced
- ✓ Restaurant owners can manage independently
- ✓ Customers can complete purchases
- ✓ System demonstrates scalability

---

## 12. Document Approval & Change Log

### 12.1 Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | Jan 12, 2026 | System Analysis | Initial BRD creation from source code analysis |

### 12.2 Next Steps

1. **Development Phase:** Features implemented per BRD requirements
2. **Testing Phase:** Functional and acceptance testing
3. **UAT Phase:** Stakeholder review and feedback
4. **Deployment Phase:** Production release planning
5. **Post-Launch:** Monitoring and optimization

---

**End of Document**
