from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # ==================== HOME & STATIC PAGES ====================
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    # ==================== BOOKS ====================
    path("books/", views.books_list_view, name="books_list"),
    path("books/<int:book_id>/", views.book_detail_view, name="book_detail"),
    # ==================== BORROWING ====================
    path("borrow/<int:book_id>/", views.borrow_view, name="borrow"),
    # ==================== CART ====================
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:book_id>/", views.add_to_cart_view, name="add_to_cart"),
    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart_view,
        name="remove_from_cart",
    ),
    # ==================== CHECKOUT ====================
    path("checkout/", views.checkout_view, name="checkout"),
    # ==================== WISHLIST ====================
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path(
        "wishlist/add/<int:book_id>/",
        views.add_to_wishlist_view,
        name="add_to_wishlist",
    ),
    path(
        "wishlist/remove/<int:book_id>/",
        views.remove_from_wishlist_view,
        name="remove_from_wishlist",
    ),
    # ==================== PROFILE ====================
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    # ==================== RATINGS ====================
    path("books/<int:book_id>/rate/", views.add_rating_view, name="add_rating"),
    # ==================== ADMIN ====================
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
]
