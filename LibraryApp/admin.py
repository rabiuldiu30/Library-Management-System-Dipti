from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Category,
    Book,
    BorrowTransaction,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
    Payment,
    Rating,
    Fine,
    ContactMessage,
)

# ==================== CUSTOM USER ADMIN ====================


class CustomUserAdmin(UserAdmin):
    """Custom admin for user management"""

    model = CustomUser

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "student_id",
        "member_type",
        "is_active",
    ]
    list_filter = ["member_type", "is_active", "is_staff", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name", "student_id"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Library Information",
            {
                "fields": (
                    "phone",
                    "student_id",
                    "member_type",
                    "profile_image",
                    "is_active_member",
                    "date_joined_library",
                )
            },
        ),
    )

    readonly_fields = ["date_joined_library"]


# ==================== CATEGORY ADMIN ====================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category management"""

    list_display = ["name", "icon"]
    search_fields = ["name"]
    ordering = ["name"]


# ==================== BOOK ADMIN ====================


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Book management"""

    list_display = [
        "title",
        "author",
        "category",
        "book_type",
        "borrow_price_per_day",
        "purchase_price",
        "is_active",
    ]
    list_filter = ["book_type", "category", "is_active", "language", "created_at"]
    search_fields = ["title", "author", "isbn", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Book Information",
            {
                "fields": (
                    "title",
                    "isbn",
                    "author",
                    "category",
                    "language",
                    "release_year",
                    "publisher",
                )
            },
        ),
        ("Description", {"fields": ("description",), "classes": ("wide",)}),
        ("Details", {"fields": ("pages", "book_type")}),
        ("Pricing", {"fields": ("borrow_price_per_day", "purchase_price")}),
        ("Media", {"fields": ("cover_image",)}),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )


# ==================== BORROW TRANSACTION ADMIN ====================


@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    """Borrow transaction management"""

    list_display = [
        "user",
        "book",
        "status",
        "borrow_date",
        "due_date",
        "return_date",
        "total_cost",
    ]
    list_filter = ["status", "delivery_method", "borrow_date", "due_date"]
    search_fields = ["user__username", "book__title", "pickup_serial_number"]
    readonly_fields = [
        "borrow_date",
        "pickup_serial_number",
        "rental_cost",
        "total_cost",
    ]
    date_hierarchy = "borrow_date"

    fieldsets = (
        ("Transaction Info", {"fields": ("user", "book", "status")}),
        (
            "Dates",
            {"fields": ("borrow_date", "due_date", "return_date", "duration_days")},
        ),
        ("Costs", {"fields": ("rental_cost", "delivery_charge", "total_cost")}),
        (
            "Delivery",
            {"fields": ("delivery_method", "pickup_serial_number", "delivery_address")},
        ),
    )


# ==================== CART ADMIN ====================


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Shopping cart management"""

    list_display = [
        "user",
        "book",
        "item_type",
        "quantity",
        "duration_days",
        "added_at",
    ]
    list_filter = ["item_type", "added_at"]
    search_fields = ["user__username", "book__title"]
    readonly_fields = ["added_at"]


# ==================== WISHLIST ADMIN ====================


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Wishlist management"""

    list_display = ["user", "get_book_count", "created_at", "updated_at"]
    search_fields = ["user__username"]
    readonly_fields = ["created_at", "updated_at"]

    def get_book_count(self, obj):
        return obj.books.count()

    get_book_count.short_description = "Total Books"


# ==================== ORDER ADMIN ====================


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order management"""

    list_display = [
        "order_number",
        "user",
        "total_amount",
        "payment_status",
        "order_status",
        "created_at",
    ]
    list_filter = ["order_status", "payment_status", "payment_method", "created_at"]
    search_fields = ["order_number", "user__username", "delivery_phone"]
    readonly_fields = ["order_number", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_number", "user", "order_status", "payment_status")},
        ),
        (
            "Customer Information",
            {
                "fields": (
                    "delivery_address",
                    "delivery_phone",
                    "delivery_city",
                    "delivery_method",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "items_total",
                    "delivery_charge",
                    "service_fee",
                    "total_amount",
                )
            },
        ),
        ("Payment", {"fields": ("payment_method", "created_at", "updated_at")}),
    )


# ==================== ORDER ITEM ADMIN ====================


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order items management"""

    list_display = ["order", "book", "item_type", "quantity", "price"]
    list_filter = ["item_type", "order__created_at"]
    search_fields = ["order__order_number", "book__title"]


# ==================== PAYMENT ADMIN ====================


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment management"""

    list_display = [
        "order",
        "amount",
        "payment_method",
        "status",
        "transaction_id",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["order__order_number", "transaction_id"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


# ==================== RATING ADMIN ====================


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Rating management"""

    list_display = ["book", "user", "rating_value", "region", "created_at"]
    list_filter = ["region", "rating_value", "created_at"]
    search_fields = ["book__title", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


# ==================== FINE ADMIN ====================


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    """Fine management"""

    list_display = [
        "user",
        "borrow_transaction",
        "fine_amount",
        "status",
        "fine_date",
        "paid_date",
    ]
    list_filter = ["status", "fine_date"]
    search_fields = ["user__username", "reason"]
    readonly_fields = ["fine_date", "paid_date"]
    date_hierarchy = "fine_date"


# ==================== CONTACT MESSAGE ADMIN ====================


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Contact message management"""

    list_display = ["subject", "email", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


# Register CustomUser
admin.site.register(CustomUser, CustomUserAdmin)
