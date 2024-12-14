from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.home, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('measurement/<int:pk>', views.customer_measurement, name='measurement'),
    path('update_measurement/<int:pk>', views.update_measurement, name='update_measurement'),
    path('add_measurement/', views.add_measurement, name='add_measurement'),
    path('delete_measurement/<int:pk>', views.delete_measurement, name='delete_measurement'),
    path('add_order/', views.add_order, name='add_order'), 
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:pk>', views.customer_order, name = 'order'),
    path('delete_order/<int:pk>', views.delete_order, name='delete_order'),
    path('update_order/<int:pk>', views.update_order, name='update_order'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
