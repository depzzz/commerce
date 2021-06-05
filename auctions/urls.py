from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.create_listing,name="create"),
    path("listing/<str:id>",views.view_listing,name="view"),
    path("listing/<str:id>/add",views.add_watchlist,name="watchlist"),
    path("listing/<str:id>/close",views.close_listing,name="close"),
    path("listing/<str:id>/comment",views.add_comment,name="comment"),
    path("watchlist",views.view_watchlist,name="view_watchlist"),
    path("categories",views.categories,name="categories"),
    path("category/<str:category>",views.category_page,name="category"),
    path("inactive",views.inactive,name="inactive"),
    path("mywins",views.my_wins,name="mywins"),
    path("mylistings",views.my_listings,name="mylistings")
]
