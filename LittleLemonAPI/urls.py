from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    # Menu-items endpoints
    path('category', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    ## path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    ## path('menu-items/<int:pk>', views.menu_items_detail, name='menu-items-detail'),

    # User group management endpoints
    path('groups/manager/users', views.manager_list),
    path('groups/manager/users/<int:userId>', views.manager_del),

    path('groups/delivery-crew/users', views.delivery_crew_list),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_crew_del),

    # Cart management endpoints 
    path('cart/menu-items', views.CartView.as_view()),

    # Order management endpoints
    # path('orders', views.OrderView.as_view()),
    path('orders', views.order_list),

    # token generation endpoints 
    path('', include('djoser.urls')),
]
