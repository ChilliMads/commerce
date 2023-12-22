from django.urls import path

from . import views

# Returns an element for inclusion in urlpatterns. See more at: Django Docs
urlpatterns = [ 
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name='create_listing'),
    path('listing_page/<int:listing_id>/', views.listing_view, name='listing'),
    path("listing/<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path('listing/<int:listing_id>/close', views.close_auction, name='close_auction'),
    path('watchlist_page/', views.watchlist_view, name='watchlist'),
    path('category_list_page/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.listings_by_category, name='listings_by_category'),
    
]
