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
    measurement_file = models.FileField(upload_to='measurements/', null=True, blank=True)

    class Meta:
        db_table = 'measurements'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.measurement_date} - {self.get_status_display()}"