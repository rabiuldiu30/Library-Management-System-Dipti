from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from .models import (
    CustomUser,
    Book,
    Category,
    BorrowTransaction,
    CartItem,
    Order,
    Rating,
    ContactMessage,
    Wishlist,
)

# ==================== AUTHENTICATION FORMS ====================


class CustomUserCreationForm(UserCreationForm):
    """Registration form for new users"""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True, label="Phone Number")
    student_id = forms.CharField(
        max_length=50, required=False, label="Student ID (Optional)"
    )
    member_type = forms.ChoiceField(
        choices=CustomUser.MEMBER_TYPE_CHOICES, required=True, label="Member Type"
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "student_id",
            "member_type",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Required. 150 characters or fewer."
        self.fields["password1"].help_text = "At least 8 characters."
        self.fields["password2"].help_text = "Enter the same password as before."

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered!")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if student_id and CustomUser.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Student ID already registered!")
        return student_id


class CustomUserLoginForm(AuthenticationForm):
    """Login form"""

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username or Email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class CustomUserChangeForm(UserChangeForm):
    """Edit user profile form"""

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "member_type",
            "profile_image",
        )


# ==================== BOOK FORMS ====================


class BookFilterForm(forms.Form):
    """Filter books by category and sort"""

    SORT_CHOICES = [
        ("popular", "Popular"),
        ("newest", "Newest"),
        ("rating", "Highest Rating"),
        ("price_low", "Price: Low to High"),
        ("price_high", "Price: High to Low"),
    ]

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="All Categories"
    )
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial="popular")
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by title or author..."}),
    )


# ==================== BORROW FORMS ====================


class BorrowTransactionForm(forms.ModelForm):
    """Form for borrowing a book"""

    duration_days = forms.IntegerField(
        initial=7,
        min_value=1,
        max_value=30,
        label="Borrow Duration (Days)",
        help_text="Maximum 30 days",
    )
    delivery_method = forms.ChoiceField(
        choices=BorrowTransaction.DELIVERY_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label="Delivery Method",
    )
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="Delivery Address (Required for Home Delivery)",
    )

    class Meta:
        model = BorrowTransaction
        fields = ["duration_days", "delivery_method", "delivery_address"]

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get("delivery_method")
        delivery_address = cleaned_data.get("delivery_address")

        if delivery_method == "delivery" and not delivery_address:
            raise forms.ValidationError(
                "Delivery address is required for home delivery!"
            )

        return cleaned_data


# ==================== CART FORMS ====================


class CartItemForm(forms.ModelForm):
    """Form for adding items to cart"""

    item_type = forms.ChoiceField(
        choices=CartItem.ITEM_TYPE_CHOICES, widget=forms.RadioSelect, label="Action"
    )
    duration_days = forms.IntegerField(
        initial=7,
        min_value=1,
        max_value=30,
        required=False,
        label="Borrow Duration (Days)",
    )

    class Meta:
        model = CartItem
        fields = ["item_type", "duration_days"]

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get("item_type")
        duration_days = cleaned_data.get("duration_days")

        if item_type == "borrow" and not duration_days:
            raise forms.ValidationError("Duration is required for borrowing!")

        return cleaned_data


class UpdateCartItemForm(forms.ModelForm):
    """Form for updating cart items"""

    quantity = forms.IntegerField(min_value=1, max_value=10)
    duration_days = forms.IntegerField(min_value=1, max_value=30, required=False)

    class Meta:
        model = CartItem
        fields = ["quantity", "duration_days"]


# ==================== CHECKOUT FORMS ====================


class CheckoutForm(forms.ModelForm):
    """Checkout form for creating orders"""

    DELIVERY_CHOICES = [
        ("pickup", "Library Pickup"),
        ("delivery", "Home Delivery (48-72 Hours)"),
    ]

    PAYMENT_CHOICES = Order.PAYMENT_METHOD_CHOICES

    full_name = forms.CharField(max_length=255, label="Full Name")
    email = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=15, label="Phone Number")
    city = forms.CharField(max_length=100, label="City")
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), label="Full Delivery Address"
    )
    delivery_method = forms.ChoiceField(
        choices=DELIVERY_CHOICES, widget=forms.RadioSelect
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing
        if self.instance.user:
            self.fields["full_name"].initial = (
                f"{self.instance.user.first_name} {self.instance.user.last_name}"
            )
            self.fields["email"].initial = self.instance.user.email
            self.fields["phone"].initial = self.instance.user.phone


class PaymentForm(forms.Form):
    """Payment form for confirming payment"""

    PAYMENT_METHOD_CHOICES = [
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("card", "Credit/Debit Card"),
        ("cod", "Cash on Delivery"),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect
    )
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        label="Transaction ID (if applicable)",
        help_text="Enter transaction ID from your payment provider",
    )


# ==================== ORDER FORMS ====================

from .models import Order


class OrderForm(forms.ModelForm):
    """Order details form"""

    class Meta:
        model = Order
        fields = [
            "delivery_address",
            "delivery_phone",
            "delivery_city",
            "delivery_method",
            "payment_method",
        ]
        widgets = {
            "delivery_address": forms.Textarea(attrs={"rows": 3}),
        }


# ==================== RATING FORMS ====================


class RatingForm(forms.ModelForm):
    """Form for rating books"""

    rating_value = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.RadioSelect(choices=[(i, "⭐" * i) for i in range(1, 6)]),
    )

    class Meta:
        model = Rating
        fields = ["rating_value", "review_text"]
        widgets = {
            "review_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Share your thoughts about this book...",
                }
            )
        }


# ==================== WISHLIST FORMS ====================


class WishlistForm(forms.Form):
    """Form for managing wishlist"""

    book_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.ChoiceField(
        choices=[("add", "Add"), ("remove", "Remove")], widget=forms.HiddenInput()
    )


# ==================== CONTACT FORMS ====================


class ContactForm(forms.ModelForm):
    """Contact form for user messages"""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your Name", "class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Your Email", "class": "form-control"}
            ),
            "subject": forms.TextInput(
                attrs={"placeholder": "Subject", "class": "form-control"}
            ),
            "message": forms.Textarea(
                attrs={
                    "placeholder": "Your Message",
                    "rows": 5,
                    "class": "form-control",
                }
            ),
        }


# ==================== SEARCH FORMS ====================


class BookSearchForm(forms.Form):
    """Advanced search form for books"""

    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by title, author, ISBN...",
                "class": "form-control",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="All Categories"
    )
    book_type = forms.ChoiceField(
        choices=[
            ("", "All Types"),
            ("borrow", "Borrow Only"),
            ("buy", "Buy Only"),
            ("both", "Both"),
        ],
        required=False,
    )
    min_price = forms.DecimalField(
        required=False, min_value=0, decimal_places=2, label="Minimum Price"
    )
    max_price = forms.DecimalField(
        required=False, min_value=0, decimal_places=2, label="Maximum Price"
    )
