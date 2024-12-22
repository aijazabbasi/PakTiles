"""
URL configuration for PakTiles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
     
    path('inventory_home/', views.inventory_home, name='inventory_home'),
    path('order_home/', views.order_home, name='order_home'),
    path('tileorder_list/', views.tileorder_list, name='tileorder_list'),
    path('tileorder_detail/<int:order_id>', views.tileorder_detail, name='tileorder_detail'),
    
    path('send_whatsapp_message_with_attachment/<int:order_id>/',views.send_whatsapp_message_with_attachment, name='send_whatsapp_message_with_attachment'),

 
 

    path('tiles/', views.list_tiles, name='list_tiles'),
    path('add_tile/', views.add_tile, name='add_tile'),
    path('edit_tile/<int:tile_id>/', views.edit_tile, name='edit_tile'),

    path('sanitary_items/', views.list_sanitary_items, name='list_sanitary_items'),
    path('add_sanitary_item/', views.add_sanitary_item, name='add_sanitary_item'),
    path('edit_sanitary_item/<int:item_id>/', views.edit_sanitary_item, name='edit_sanitary_item'),
    
    path('create_order/', views.create_order, name='create_order'),
    path('create_sanitaryorder/', views.create_sanitaryorder, name='create_sanitaryorder'),
    
    path('get_tile_data/', views.get_tile_data, name='get_tile_data'),
    path('get_sanitary_data/', views.get_sanitary_data, name='get_sanitary_data'),
    path('get_available_stock/', views.get_available_stock, name='get_available_stock'),
    
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    
 
    path('signup/', views.signup, name='signup'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
