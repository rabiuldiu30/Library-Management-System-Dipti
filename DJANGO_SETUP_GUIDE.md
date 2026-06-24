# LibraryPro Django Application - Setup Guide

## ✅ Implementation Complete

Your LibraryPro website has been successfully converted into a **production-ready Django application** with the following components:

---

## 📦 **What Has Been Created**

### 1. **Database Models (models.py)** ✅

- `CustomUser` - Extended user with library-specific fields
- `Category` - Book categories
- `Book` - Complete book catalog
- `BorrowTransaction` - Book borrowing records with auto-generated serial numbers
- `CartItem` - Shopping cart management
- `Wishlist` - User wishlists
- `Order` & `OrderItem` - Purchase orders
- `Payment` - Payment records (mocked)
- `Rating` - Book ratings (World + Bangladesh)
- `Fine` - Late return fines (৳5/day)
- `ContactMessage` - Contact form submissions

### 2. **Django Forms (forms.py)** ✅

- `CustomUserCreationForm` - Registration
- `CustomUserLoginForm` - Login
- `BorrowTransactionForm` - Borrowing options
- `CartItemForm` - Add to cart
- `CheckoutForm` - Order checkout
- `RatingForm` - Book ratings
- `ContactForm` - Contact messages
- `BookSearchForm` - Advanced search

### 3. **Views (views.py)** ✅

- Authentication views (register, login, logout)
- Book catalog with search & filtering
- Book details page
- Borrow system with multiple delivery methods
- Shopping cart management
- Checkout process with auto-generated order numbers
- Wishlist management
- User profile with stats
- Rating system
- Admin dashboard

### 4. **URL Routing (urls.py)** ✅

- All endpoints configured
- RESTful URL structure
- Named URLs for templates

### 5. **Django Admin (admin.py)** ✅

- Complete admin interface for all models
- Custom filters and search
- Readonly fields configuration
- Organized fieldsets

### 6. **Project Configuration** ✅

- `settings.py` updated with:
  - Custom user model configuration
  - Media file handling
  - Static file configuration
  - Timezone set to Asia/Dhaka
  - Login URLs configured
- `urls.py` configured with media file serving

### 7. **Base Template (base.html)** ✅

- Responsive navbar with search
- Messages display system
- Authenticated/unauthenticated navbar links
- Footer with navigation
- All templates extend this base

---

## 🚀 **How to Run the Application**

### **Step 1: Install Required Packages**

```bash
pip install pillow  # For image handling
```

### **Step 2: Create Migrations**

```bash
python manage.py makemigrations
```

**Expected Output:**

```
Migrations for 'LibraryApp':
  LibraryApp\migrations\0001_initial.py
    - Create model CustomUser
    - Create model Category
    - Create model Book
    - ...and more models
```

### **Step 3: Apply Migrations**

```bash
python manage.py migrate
```

**Expected Output:**

```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying LibraryApp.0001_initial... OK
```

### **Step 4: Create Superuser (Admin)**

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:

- Username: `admin`
- Email: `admin@librarypro.com`
- Password: (enter a secure password)
- Password confirmation

### **Step 5: Run Development Server**

```bash
python manage.py runserver
```

**Expected Output:**

```
Starting development server at http://127.0.0.1:8000/
```

---

## 🌐 **Access the Application**

### **Frontend**

- **Home Page:** http://127.0.0.1:8000/
- **Books Catalog:** http://127.0.0.1:8000/books/
- **Book Details:** http://127.0.0.1:8000/books/1/
- **Cart:** http://127.0.0.1:8000/cart/
- **Checkout:** http://127.0.0.1:8000/checkout/
- **Wishlist:** http://127.0.0.1:8000/wishlist/
- **Profile:** http://127.0.0.1:8000/profile/ (requires login)
- **Login:** http://127.0.0.1:8000/login/
- **Register:** http://127.0.0.1:8000/register/
- **About:** http://127.0.0.1:8000/about/
- **Contact:** http://127.0.0.1:8000/contact/

### **Admin Panel**

- **URL:** http://127.0.0.1:8000/admin/
- **Username:** admin
- **Password:** (the one you created)

---

## 📊 **Database Operations in Admin**

### **Adding Sample Data**

#### **1. Add Book Categories**

1. Go to Admin → Categories → Add Category
2. Enter: Name = "Programming", Icon = "fa-code"
3. Repeat for: Science, Novel, Business

#### **2. Add Books**

1. Go to Admin → Books → Add Book
2. Fill in:
   - Title: "HTML Complete Guide"
   - Author: "John Smith"
   - Category: "Programming"
   - Description: (any text)
   - Book Type: "Both Borrow & Buy"
   - Borrow Price per Day: 20
   - Purchase Price: 550
   - Release Year: 2024
   - Language: English
   - Pages: 450

#### **3. Add Users (via Registration)**

- Register at `/register/` or create via Admin panel

#### **4. Manage Orders**

- Orders appear automatically after checkout
- View/edit in Admin → Orders

---

## 🔑 **Key Features Implemented**

### **✅ User Authentication**

- Registration with phone, student ID, member type
- Login/logout with session management
- Profile management
- Wishlist per user

### **✅ Book Management**

- Full catalog with metadata
- Dual ratings (World + Bangladesh)
- Search by title, author, ISBN
- Filter by category
- Sort by popular, newest, rating, price

### **✅ Borrowing System**

- Two delivery methods (Pickup/Home Delivery)
- Auto-generated pickup serial numbers (LP-2026-XXXXXX)
- Automatic due date calculation (7 days default)
- Cost calculation with delivery charges
- Overdue tracking
- Fine calculation (৳5/day)

### **✅ Shopping & Checkout**

- Add to cart (borrow or buy)
- Multiple payment methods (bKash, Nagad, Card, COD)
- Order number auto-generation (ORD-XXXXXX)
- Order tracking
- Order history in profile

### **✅ Admin Dashboard**

- Manage books, users, orders, borrows
- View statistics
- Track deliveries
- Fine management

---

## 📝 **Important Notes**

### **Auto-Generated Values**

- **Pickup Serial Numbers:** `LP-YYYYMMDDHHMMSS-XXXXXX`
- **Order Numbers:** `ORD-YYYYMMDDHHMM-XXXXXX`
- **Due Dates:** Auto-calculated based on duration
- **Rental Costs:** Auto-calculated as price_per_day × duration_days

### **Payment System**

- Payment is **mocked** (recorded but not processed)
- To integrate real payment: Update `checkout_view` in views.py

### **Fine Calculation**

- Automatic fine creation when return_date > due_date
- Fine amount: ৳5 × number of days overdue

### **SQLite3 Database**

- Located at: `LibraryProject/db.sqlite3`
- Perfect for development
- For production, migrate to PostgreSQL/MySQL

---

## 🛠️ **Common Management Commands**

```bash
# Create superuser
python manage.py createsuperuser

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver

# Create app (if needed)
python manage.py startapp app_name

# Shell access (for database queries)
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic

# Clear migrations (if needed)
python manage.py migrate LibraryApp zero
```

---

## 📋 **Templates That Need Completion**

The following templates extend `base.html` and need Django syntax conversion:

**Priority 1 (High):**

- [ ] `pages/books.html` - Book listing with filters
- [ ] `pages/book-details.html` - Detailed book view
- [ ] `pages/cart.html` - Shopping cart
- [ ] `pages/checkout.html` - Checkout form
- [ ] `pages/profile.html` - User dashboard

**Priority 2 (Medium):**

- [ ] `pages/borrow.html` - Borrow options
- [ ] `pages/wishlist.html` - Wishlist display
- [ ] `accounts/login.html` - Login form
- [ ] `accounts/register.html` - Registration form

**Priority 3 (Low):**

- [ ] `pages/about.html` - Static content
- [ ] `pages/contact.html` - Contact form
- [ ] `pages/admin-dashboard.html` - Admin panel

---

## 🔐 **Security Tips**

1. **Change SECRET_KEY** in `settings.py` before production
2. **Set DEBUG = False** for production
3. **Use environment variables** for sensitive data
4. **Add CSRF protection** to all forms (already included)
5. **Use HTTPS** in production

---

## 📚 **Project Structure**

```
LibraryProject/
├── LibraryApp/
│   ├── migrations/          # Database migrations
│   ├── templates/
│   │   ├── base.html       # Base template
│   │   ├── accounts/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── pages/
│   │       ├── index.html  (converted ✅)
│   │       ├── books.html
│   │       ├── book-details.html
│   │       └── ...more pages
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/
│   │   └── images/
│   ├── admin.py            # Admin configuration ✅
│   ├── models.py           # Database models ✅
│   ├── forms.py            # Django forms ✅
│   ├── views.py            # View functions ✅
│   ├── urls.py             # URL routing ✅
│   └── apps.py
├── LibraryProject/
│   ├── settings.py         # Updated ✅
│   ├── urls.py             # Updated ✅
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── db.sqlite3              # Database (created after migrate)
```

---

## ✨ **Next Steps**

1. **Run migrations** to create database tables
2. **Create superuser** for admin access
3. **Add sample books** via admin panel
4. **Complete template conversion** (see list above)
5. **Test user registration** and login
6. **Test checkout** with mock payment
7. **Deploy** to production server

---

## 💡 **Customization Options**

### **Add Email Notifications**

```python
# In views.py - after order creation
send_mail('Order Confirmation', message, 'from@example.com', [user.email])
```

### **Add Real Payment Gateway**

```python
# In checkout_view - modify Payment integration
stripe.Charge.create(amount=total_amount, currency='bdt', source=token)
```

### **Change Fine Amount**

Edit in `models.py` - `BorrowTransaction.save()` method or use a settings constant

### **Extend User Profile**

Add more fields to `CustomUser` model in `models.py`

---

## 🆘 **Troubleshooting**

### **"No such table" error**

```bash
python manage.py migrate
```

### **"Module not found" error**

```bash
pip install pillow  # For image handling
pip install Pillow  # If pillow fails
```

### **Images not displaying**

Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in `settings.py` ✅

### **CSS/JS not loading**

Run: `python manage.py collectstatic`

---

## 📞 **Support**

For questions about:

- **Models:** Check `LibraryApp/models.py` - all models have docstrings
- **Views:** Check `LibraryApp/views.py` - all views have comments
- **Forms:** Check `LibraryApp/forms.py` - all forms are documented
- **Admin:** Check `LibraryApp/admin.py` - admin classes are organized

---

**Your LibraryPro Django application is ready for development! 🎉**
