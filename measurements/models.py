from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

class Master(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'masters'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Measurement(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('under_review', 'Рассмотрение'),
        ('rejected', 'Отказ'),
        ('accepted', 'Принят'),
    ]

    created_at = models.DateTimeField(auto_now_add=True) 
    measurement_date = models.DateTimeField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    file_measurement = models.FileField(
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf'],
                message=_("Разрешены только PDF файлы.")
            )
        ]
    )
    class Meta:
        db_table = 'measurements'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.measurement_date} - {self.get_status_display()}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)  
    cost = models.DecimalField(max_digits=10, decimal_places=2)  
    created_at = models.DateTimeField(auto_now_add=True)  
    execution_date = models.DateTimeField() 
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True)  
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending') 

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Заказ #{self.id} - {self.measurement} - Стоимость: {self.cost} ₽"
