from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.utils import timezone

# ==================== CUSTOM USER MODEL ====================


class CustomUser(AbstractUser):
    """Extended User model with library-specific fields"""

    MEMBER_TYPE_CHOICES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("general", "General Member"),
    ]

    phone = models.CharField(max_length=15, blank=True)
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    member_type = models.CharField(
        max_length=20, choices=MEMBER_TYPE_CHOICES, default="student"
    )
    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    date_joined_library = models.DateTimeField(auto_now_add=True)
    is_active_member = models.BooleanField(default=True)

    class Meta:
        db_table = "custom_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name}" if self.first_name else self.username
        )

    def get_borrowed_books_count(self):
        """Get total books borrowed by user"""
        return BorrowTransaction.objects.filter(user=self, status="completed").count()

    def get_active_borrows_count(self):
        """Get currently active borrows"""
        return BorrowTransaction.objects.filter(user=self, status="active").count()

    def get_total_fine_due(self):
        """Get total outstanding fines"""
        fines = Fine.objects.filter(user=self, status="unpaid")
        return sum(fine.fine_amount for fine in fines)


# ==================== BOOK CATALOG ====================


class Category(models.Model):
    """Book categories"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For Font Awesome icons

    class Meta:
        db_table = "category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book catalog"""

    BOOK_TYPE_CHOICES = [
        ("borrow", "Borrow Only"),
        ("buy", "Buy Only"),
        ("both", "Both Borrow & Buy"),
    ]

    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="books"
    )

    # Book metadata
    description = models.TextField()
    pages = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default="English")
    release_year = models.IntegerField()
    publisher = models.CharField(max_length=255, blank=True)
    book_type = models.CharField(
        max_length=10, choices=BOOK_TYPE_CHOICES, default="both"
    )

    # Pricing
    borrow_price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, default=20, validators=[MinValueValidator(0)]
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    # Images
    cover_image = models.ImageField(upload_to="books/", null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "book"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["category"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.title

    def get_world_rating(self):
        """Get average world rating"""
        ratings = self.ratings.filter(region="world")
        if ratings.exists():
            avg = ratings.aggregate(models.Avg("rating_value"))["rating_value__avg"]
            return round(avg, 1) if avg else 0
        return 0

    def get_bangladesh_rating(self):
        """Get average Bangladesh rating"""
        ratings = self.ratings.filter(region="bangladesh")
        if ratings.exists():
            avg = ratings.aggregate(models.Avg("rating_value"))["rating_value__avg"]
            return round(avg, 1) if avg else 0
        return 0


# ==================== BORROW SYSTEM ====================


class BorrowTransaction(models.Model):
    """Book borrowing records"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active Borrow"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    DELIVERY_METHOD_CHOICES = [
        ("pickup", "Library Pickup"),
        ("delivery", "Home Delivery"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="borrow_transactions"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrow_transactions"
    )

    # Dates
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    # Duration and cost
    duration_days = models.IntegerField(default=7, validators=[MinValueValidator(1)])
    rental_cost = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    # Delivery
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_METHOD_CHOICES, default="pickup"
    )
    pickup_serial_number = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )
    delivery_address = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "borrow_transaction"
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

    def save(self, *args, **kwargs):
        """Auto-calculate dates and costs"""
        if not self.due_date and self.duration_days:
            self.due_date = (timezone.now() + timedelta(days=self.duration_days)).date()

        if not self.rental_cost and self.book and self.duration_days:
            self.rental_cost = (
                float(self.book.borrow_price_per_day) * self.duration_days
            )

        if not self.total_cost:
            self.total_cost = float(self.rental_cost) + float(self.delivery_charge)

        # Generate pickup serial if needed
        if self.delivery_method == "pickup" and not self.pickup_serial_number:
            import uuid

            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            random_num = str(uuid.uuid4())[:6].upper()
            self.pickup_serial_number = f"LP-{timestamp}-{random_num}"

        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if book is overdue"""
        if self.status in ["active", "overdue"]:
            return timezone.now().date() > self.due_date
        return False

    def get_days_overdue(self):
        """Get number of days overdue"""
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0


# ==================== SHOPPING CART ====================


class CartItem(models.Model):
    """Shopping cart items"""

    ITEM_TYPE_CHOICES = [
        ("borrow", "Borrow"),
        ("buy", "Buy"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="cart_items"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    item_type = models.CharField(
        max_length=10, choices=ITEM_TYPE_CHOICES, default="borrow"
    )
    quantity = models.IntegerField(default=1)
    duration_days = models.IntegerField(default=7, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_item"
        unique_together = ("user", "book", "item_type")

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def get_item_price(self):
        """Calculate item price"""
        if self.item_type == "borrow":
            return float(self.book.borrow_price_per_day) * self.duration_days
        else:  # buy
            return float(self.book.purchase_price) if self.book.purchase_price else 0


# ==================== WISHLISTS ====================


class Wishlist(models.Model):
    """User wishlist for favorite books"""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="wishlist"
    )
    books = models.ManyToManyField(Book, related_name="wishlisted_by", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wishlist"

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    def add_book(self, book):
        """Add book to wishlist"""
        self.books.add(book)

    def remove_book(self, book):
        """Remove book from wishlist"""
        self.books.remove(book)


# ==================== ORDERS & PAYMENTS ====================


class Order(models.Model):
    """Purchase orders"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("card", "Credit/Debit Card"),
        ("cod", "Cash on Delivery"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="orders"
    )
    order_number = models.CharField(max_length=50, unique=True)

    # Delivery
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=15)
    delivery_city = models.CharField(max_length=100)
    delivery_method = models.CharField(
        max_length=20,
        choices=[("pickup", "Library Pickup"), ("delivery", "Home Delivery")],
        default="pickup",
    )

    # Pricing
    items_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )

    # Status
    order_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        """Generate order number if not exists"""
        if not self.order_number:
            import uuid

            timestamp = timezone.now().strftime("%Y%m%d%H%M")
            random_suffix = str(uuid.uuid4())[:6].upper()
            self.order_number = f"ORD-{timestamp}-{random_suffix}"

        # Calculate total
        if not self.total_amount:
            self.total_amount = (
                float(self.items_total)
                + float(self.delivery_charge)
                + float(self.service_fee)
            )

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual items in an order"""

    ITEM_TYPE_CHOICES = [
        ("borrow", "Borrow"),
        ("buy", "Buy"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    quantity = models.IntegerField(default=1)
    duration_days = models.IntegerField(default=7, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.order.order_number} - {self.book.title}"


class Payment(models.Model):
    """Payment records"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    payment_method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )

    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.status}"


# ==================== RATINGS & REVIEWS ====================


class Rating(models.Model):
    """Book ratings"""

    REGION_CHOICES = [
        ("world", "World Rating"),
        ("bangladesh", "Bangladesh Rating"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="ratings"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    rating_value = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="world")
    review_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rating"
        unique_together = ("user", "book", "region")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book.title} - {self.rating_value}★ ({self.region})"


# ==================== FINES ====================


class Fine(models.Model):
    """Late return fines"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("waived", "Waived"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="fines")
    borrow_transaction = models.ForeignKey(
        BorrowTransaction,
        on_delete=models.CASCADE,
        related_name="fines",
        null=True,
        blank=True,
    )

    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")

    fine_date = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)

    reason = models.TextField(blank=True)

    class Meta:
        db_table = "fine"
        ordering = ["-fine_date"]

    def __str__(self):
        return f"Fine ৳{self.fine_amount} - {self.user.username} ({self.status})"


# ==================== CONTACT MESSAGES ====================


class ContactMessage(models.Model):
    """Contact form submissions"""

    STATUS_CHOICES = [
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("resolved", "Resolved"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contact_message"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.email}"
