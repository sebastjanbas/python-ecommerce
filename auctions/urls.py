from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing_view, name="add_listing"),
    path("<int:listing_id>", views.listing_view, name="listing"),
    path("<int:listing_id>/bid", views.update_bid, name="bid"),
    path("watch_list/", views.watch_list, name="watch_list"),
    path("<int:listing_id>/add", views.add_to_watchlist, name="add_to_watchlist"),
    path("<int:listing_id>/remove", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_listings, name="category_listings"),
]
