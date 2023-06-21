from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('category', views.CategoriesView.as_view()),

    path('menu-items', views.MenuItemsView.as_view()),
    # path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    # path('menu-items/<int:pk>', views.menu_items_detail, name='menu-items-detail'),
    
    path('', include('djoser.urls')),
]
