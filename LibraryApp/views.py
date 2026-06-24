from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    CustomUser, Book, Category, BorrowTransaction, CartItem, 
    Wishlist, Order, OrderItem, Payment, Rating, Fine, ContactMessage
)
from .forms import (
    CustomUserCreationForm, CustomUserLoginForm, CustomUserChangeForm,
    BorrowTransactionForm, CartItemForm, CheckoutForm, RatingForm,
    ContactForm, BookSearchForm
)

# ==================== AUTHENTICATION VIEWS ====================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('library:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            Wishlist.objects.create(user=user)
            login(request, user)

            messages.success(request, "Registration successful!")

            print("USER CREATED:", user.username)  # DEBUG

            return redirect('library:home')
        else:
            print(form.errors)  # DEBUG show errors in terminal
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ==================== HOME & STATIC PAGES ====================

def home_view(request):
    """Home page with featured books"""
    featured_books = Book.objects.filter(is_active=True).order_by('-created_at')[:6]
    categories = Category.objects.all()
    
    context = {
        'featured_books': featured_books,
        'categories': categories,
        'total_books': Book.objects.filter(is_active=True).count(),
        'total_members': CustomUser.objects.count(),
    }
    return render(request, 'pages/index.html', context)


def about_view(request):
    """About page"""
    stats = {
        'total_books': Book.objects.filter(is_active=True).count(),
        'total_users': CustomUser.objects.count(),
        'total_borrows': BorrowTransaction.objects.filter(status='completed').count(),
    }
    return render(request, 'pages/about.html', {'stats': stats})


def contact_view(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})


# ==================== BOOK CATALOG VIEWS ====================

def books_list_view(request):
    """Display all books with filtering and search"""
    books = Book.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        books = books.annotate(avg_rating=Avg('ratings__rating_value')).order_by('-avg_rating')
    elif sort_by == 'rating':
        books = books.annotate(avg_rating=Avg('ratings__rating_value')).order_by('-avg_rating')
    elif sort_by == 'price_low':
        books = books.order_by('borrow_price_per_day')
    elif sort_by == 'price_high':
        books = books.order_by('-borrow_price_per_day')
    else:  # newest
        books = books.order_by('-created_at')
    
    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'pages/books.html', context)


def book_detail_view(request, book_id):
    """Display book details"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    ratings = book.ratings.all()
    world_rating = book.get_world_rating()
    bangladesh_rating = book.get_bangladesh_rating()
    
    # Get user's rating if exists
    user_rating = None
    if request.user.is_authenticated:
        user_rating = book.ratings.filter(user=request.user).first()
    
    context = {
        'book': book,
        'ratings': ratings,
        'world_rating': world_rating,
        'bangladesh_rating': bangladesh_rating,
        'user_rating': user_rating,
    }
    return render(request, 'pages/book-details.html', context)


# ==================== BORROW VIEWS ====================

@login_required
def borrow_view(request, book_id):
    """Borrow book page with options"""
    book = get_object_or_404(Book, id=book_id, is_active=True)
    
    if request.method == 'POST':
        form = BorrowTransactionForm(request.POST)
        if form.is_valid():
            borrow = BorrowTransaction.objects.create(
                user=request.user,
                book=book,
                duration_days=form.cleaned_data['duration_days'],
                delivery_method=form.cleaned_data['delivery_method'],
                delivery_address=form.cleaned_data.get('delivery_address', ''),
                status='active'
            )
            messages.success(request, 'Book borrowed successfully!')
            return redirect('profile')
    else:
        form = BorrowTransactionForm()
    
    # Calculate cost
    default_days = 7
    rental_cost = float(book.borrow_price_per_day) * default_days
    delivery_charge = 30
    total_cost = rental_cost + delivery_charge
    
    context = {
        'book': book,
        'form': form,
        'default_days': default_days,
        'rental_cost': rental_cost,
        'delivery_charge': delivery_charge,
        'total_cost': total_cost,
    }
    return render(request, 'pages/borrow.html', context)


# ==================== CART VIEWS ====================

@login_required
def add_to_cart_view(request, book_id):
    """Add book to cart"""
    book = get_object_or_404(Book, id=book_id)
    item_type = request.GET.get('type', 'borrow')
    duration_days = int(request.GET.get('duration', 7))
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        book=book,
        item_type=item_type,
        defaults={'duration_days': duration_days}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.duration_days = duration_days
        cart_item.save()
    
    messages.success(request, f'"{book.title}" added to cart!')
    return redirect(request.GET.get('next', 'cart'))


@login_required
def cart_view(request):
    """View shopping cart"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate totals
    items_total = sum(item.get_item_price() for item in cart_items)
    delivery_charge = 30 if cart_items.exists() else 0
    service_fee = 10 if cart_items.exists() else 0
    total_amount = items_total + delivery_charge + service_fee
    
    context = {
        'cart_items': cart_items,
        'items_total': items_total,
        'delivery_charge': delivery_charge,
        'service_fee': service_fee,
        'total_amount': total_amount,
    }
    return render(request, 'pages/cart.html', context)


@login_required
@require_POST
def remove_from_cart_view(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f'"{book_title}" removed from cart.')
    return redirect('cart')


# ==================== CHECKOUT VIEWS ====================

@login_required
def checkout_view(request):
    """Checkout page"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('books_list')
    
    # Calculate totals
    items_total = sum(item.get_item_price() for item in cart_items)
    delivery_charge = 30
    service_fee = 10
    total_amount = items_total + delivery_charge + service_fee
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                delivery_address=form.cleaned_data['delivery_address'],
                delivery_phone=form.cleaned_data['phone'],
                delivery_city=form.cleaned_data['city'],
                delivery_method=form.cleaned_data['delivery_method'],
                payment_method=form.cleaned_data['payment_method'],
                items_total=items_total,
                delivery_charge=delivery_charge,
                service_fee=service_fee,
                total_amount=total_amount,
                order_status='confirmed',
                payment_status='completed'
            )
            
            # Create order items from cart
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    item_type=cart_item.item_type,
                    quantity=cart_item.quantity,
                    duration_days=cart_item.duration_days if cart_item.item_type == 'borrow' else None,
                    price=cart_item.get_item_price()
                )
                
                # Create borrow transaction if item type is borrow
                if cart_item.item_type == 'borrow':
                    BorrowTransaction.objects.create(
                        user=request.user,
                        book=cart_item.book,
                        duration_days=cart_item.duration_days,
                        status='active'
                    )
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=form.cleaned_data['payment_method'],
                amount=total_amount,
                status='completed'
            )
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('profile')
    else:
        form = CheckoutForm(initial={
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email,
            'phone': request.user.phone,
        })
    
    context = {
        'cart_items': cart_items,
        'form': form,
        'items_total': items_total,
        'delivery_charge': delivery_charge,
        'service_fee': service_fee,
        'total_amount': total_amount,
    }
    return render(request, 'pages/checkout.html', context)


# ==================== WISHLIST VIEWS ====================

@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist = get_object_or_404(Wishlist, user=request.user)
    books = wishlist.books.all()
    
    context = {
        'books': books,
        'wishlist': wishlist,
    }
    return render(request, 'pages/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist_view(request, book_id):
    """Add book to wishlist"""
    book = get_object_or_404(Book, id=book_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if not wishlist.books.filter(id=book_id).exists():
        wishlist.add_book(book)
        messages.success(request, f'"{book.title}" added to wishlist!')
    else:
        messages.info(request, f'"{book.title}" is already in your wishlist.')
    
    return redirect(request.GET.get('next', 'book_detail') if request.GET.get('next') == 'book_detail' else 'wishlist')


@login_required
@require_POST
def remove_from_wishlist_view(request, book_id):
    """Remove book from wishlist"""
    book = get_object_or_404(Book, id=book_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if wishlist.books.filter(id=book_id).exists():
        wishlist.remove_book(book)
        messages.success(request, f'"{book.title}" removed from wishlist.')
    
    return redirect('wishlist')


# ==================== PROFILE VIEWS ====================

@login_required
def profile_view(request):
    """User profile page"""
    user = request.user
    borrow_transactions = BorrowTransaction.objects.filter(user=user).order_by('-borrow_date')[:5]
    wishlist = get_object_or_404(Wishlist, user=user)
    favorite_books = wishlist.books.all()[:4]
    
    # Calculate stats
    total_borrowed = user.get_borrowed_books_count()
    active_borrows = user.get_active_borrows_count()
    total_fine = user.get_total_fine_due()
    
    context = {
        'user': user,
        'borrow_transactions': borrow_transactions,
        'favorite_books': favorite_books,
        'total_borrowed': total_borrowed,
        'active_borrows': active_borrows,
        'total_fine': total_fine,
    }
    return render(request, 'pages/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'pages/profile-edit.html', {'form': form})


# ==================== RATING VIEWS ====================

@login_required
@require_POST
def add_rating_view(request, book_id):
    """Add or update book rating"""
    book = get_object_or_404(Book, id=book_id)
    form = RatingForm(request.POST)
    
    if form.is_valid():
        rating_obj, created = Rating.objects.update_or_create(
            user=request.user,
            book=book,
            region='world',
            defaults={'rating_value': form.cleaned_data['rating_value']}
        )
        
        if form.cleaned_data.get('review_text'):
            rating_obj.review_text = form.cleaned_data['review_text']
            rating_obj.save()
        
        action = "added" if created else "updated"
        messages.success(request, f'Rating {action} successfully!')
    else:
        messages.error(request, 'Please provide a valid rating.')
    
    return redirect('book_detail', book_id=book_id)


# ==================== ADMIN DASHBOARD VIEWS ====================

@login_required
def admin_dashboard_view(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    stats = {
        'total_books': Book.objects.count(),
        'total_users': CustomUser.objects.count(),
        'active_borrows': BorrowTransaction.objects.filter(status='active').count(),
        'pending_orders': Order.objects.filter(order_status='pending').count(),
    }
    
    recent_orders = Order.objects.all()[:10]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
    }
    return render(request, 'pages/admin-dashboard.html', context)
