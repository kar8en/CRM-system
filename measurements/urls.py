from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('measurement/<int:pk>', views.customer_measurement, name='measurement'),
    path('update_measurement/<int:pk>', views.update_measurement, name='update_measurement'),
    path('add_measurement/', views.add_measurement, name='add_measurement'),
    path('delete_measurement/<int:pk>', views.delete_measurement, name='delete_measurement'),
   
]
