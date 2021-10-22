from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("comments", views.comments, name="comments"),
    path("categories/", views.categories, name="categories"),
    path("active", views.active, name="active"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories/<int:category_id>", views.category, name="category_id")
]

urlpatterns += staticfiles_urlpatterns()