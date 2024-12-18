from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddMeasurementForm, AddOrderForm
from .models import Measurement, Master, Order
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from django.conf import settings
import os
import boto3
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render


def home(request):
    masters = Master.objects.all()
    measurements = Measurement.objects.all()

    selected_master = request.GET.getlist('master')
    selected_status = request.GET.getlist('status')
    address_query = request.GET.get('address', '')

    if selected_master:
        measurements = measurements.filter(master_id__in=selected_master)

    if selected_status:
        measurements = measurements.filter(status__in=selected_status)

    if address_query:
        measurements = measurements.filter(address__icontains=address_query)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Вы успешно вошли в систему")
            return redirect('home')
        else:
            messages.error(request, "Ошибка. Попробуйте войти снова")
            return redirect('home')

    context = {
        'measurements': measurements,
        'masters': masters,
        'selected_master': selected_master,
        'selected_status': selected_status,
        'address_query': address_query,
        'STATUS_CHOICES': Measurement.STATUS_CHOICES,
    }

    return render(request, 'home.html', context)

def logout_user(request):
	logout(request)
	messages.success(request, "Вы успешно вышли из системы")
	return redirect('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "Вы успешно зарегестрировались!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})

def customer_measurement(request, pk):
	if request.user.is_authenticated:
		customer_measurement = Measurement.objects.get(id=pk)
		return render(request, 'measurement.html', {'customer_measurement':customer_measurement})
	else:
		messages.success(request, "Необходимо войти в систему")
		return redirect('home')

def customer_order(request, pk):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=pk)
        return render(request, 'order.html', {'order': order})
    else:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')

class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_path: str, object_name): 
        try:
            async with self.get_client() as client:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=file,
                    )
                print(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")


# def add_measurement(request):
#     if not request.user.is_authenticated:
#         messages.error(request, "Необходимо войти в систему")
#         return redirect('home')

#     if request.method == "POST":
#         form = AddMeasurementForm(request.POST, request.FILES)
#         if form.is_valid():
#             measurement = form.save(commit=False)
#             if request.FILES.get('file_measurement'):
#                 file = request.FILES['file_measurement']
#                 fs = FileSystemStorage()
#                 filename = fs.save(file.name, file) 
#                 full_path = os.path.join(fs.location, filename)
#                 measurement.save()
#                 key = f"measurement_{measurement.id}.pdf"
#                 async def main():
#                     s3_client = S3Client(
#                             access_key=f'{settings.AWS_ACCESS_KEY_ID}',
#                             secret_key=f'{settings.AWS_SECRET_ACCESS_KEY}',
#                             endpoint_url=f'{settings.URL}',  
#                             bucket_name=f'{settings.AWS_STORAGE_BUCKET_NAME}',
#                     )
#                     await s3_client.upload_file(full_path, key)
#                     if os.path.exists(full_path):
#                         os.remove(full_path)
#                 asyncio.run(main())
#                 measurement.file_measurement = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
#             measurement.save()
#             messages.success(request, "Замер добавлен")
#             return redirect('home')
#     else:
#         form = AddMeasurementForm()

#     return render(request, 'add_measurement.html', {'form': form})

def upload_file_to_s3(file_path, bucket_name, key):
    """Функция для загрузки файла в S3."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.URL,
    )
    
    try:
        s3_client.upload_file(file_path, bucket_name, key)
        return True
    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        return False

def add_measurement(request):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')

    if request.method == "POST":
        form = AddMeasurementForm(request.POST, request.FILES)
        if form.is_valid():
            measurement = form.save(commit=False)

            if request.FILES.get('file_measurement'):
                file = request.FILES['file_measurement']
                fs = FileSystemStorage()
                
                
                filename = fs.save(file.name, file)
                full_path = os.path.join(fs.location, filename)
                measurement.save()
                key = f"measurement_{measurement.id}.pdf"

                
                if upload_file_to_s3(full_path, settings.AWS_STORAGE_BUCKET_NAME, key):
                    measurement.file_measurement = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
                    
                    try:
                        os.remove(full_path)
                        print(f"Файл {full_path} успешно удален.")
                    except Exception as e:
                        print(f"Ошибка при удалении файла: {str(e)}")
                    
                    messages.success(request, "Замер добавлен")
                    measurement.save()
                    return redirect('home')
                else:
                    messages.error(request, "Ошибка при загрузке файла.")
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            print(f"Файл {full_path} успешно удален.")
                        except Exception as e:
                            print(f"Ошибка при удалении файла: {str(e)}")
            
    else:
        form = AddMeasurementForm()

    return render(request, 'add_measurement.html', {'form': form})

def delete_measurement(request, pk):
    if request.user.is_authenticated:
        measurement_to_delete = get_object_or_404(Measurement, id=pk)
        measurement_to_delete.delete()
        messages.success(request, "Замер успешно удален")
        return redirect('home')
    else:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')


def update_measurement(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')
    current_measurement = get_object_or_404(Measurement, id=pk)
    if request.method == "POST":
        form = AddMeasurementForm(request.POST, request.FILES, instance=current_measurement)
        if form.is_valid():
            measurement = form.save(commit=False)
            if request.FILES.get('file_measurement'):
                file = request.FILES['file_measurement']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                full_path = os.path.join(fs.location, filename)

                key = f"measurement_{measurement.id}.pdf"
                if upload_file_to_s3(full_path, settings.AWS_STORAGE_BUCKET_NAME, key):
                    measurement.file_measurement = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"
                    
                    try:
                        os.remove(full_path)
                        print(f"Файл {full_path} успешно удален.")
                    except Exception as e:
                        print(f"Ошибка при удалении файла: {str(e)}")
                    
                    messages.success(request, "Замер обновлен")
                    measurement.save()
                    return redirect('home')
                else:
                    messages.error(request, "Ошибка при загрузке файла.")
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            print(f"Файл {full_path} успешно удален.")
                        except Exception as e:
                            print(f"Ошибка при удалении файла: {str(e)}")

    else:
        form = AddMeasurementForm(instance=current_measurement)

    return render(request, 'update_measurement.html', {'form': form})

def add_order(request):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')

    if request.method == "POST":
        form = AddOrderForm(request.POST)
        
        if form.is_valid():
            measurement_id = form.cleaned_data['measurement_id']
            try:
                measurement = Measurement.objects.get(id=measurement_id)
            except Measurement.DoesNotExist:
                messages.error(request, "Замер с таким номером не найден.")
                return render(request, 'add_order.html', {'form': form})

            order = Order(
                measurement=measurement,
                cost=form.cleaned_data['cost'],
                execution_date=form.cleaned_data['execution_date'],
                master=form.cleaned_data['master'],
                status=form.cleaned_data['status']
            )
            order.save()
            messages.success(request, "Заказ добавлен")
            return redirect('order_list')
    else:
        form = AddOrderForm()

    return render(request, 'add_order.html', {'form': form})



def order_list(request):
    masters = Master.objects.all()  
    orders = Order.objects.all()  
    
    selected_master = request.GET.getlist('master')
    selected_status = request.GET.getlist('status')

    orders = filter_orders(orders, selected_master, selected_status)

    if request.method == 'POST':
        return handle_login(request)

    context = {
        'orders': orders,
        'masters': masters,
        'selected_master': selected_master,
        'selected_status': selected_status,
        'STATUS_CHOICES': Order.ORDER_STATUS_CHOICES,  
    }

    return render(request, 'order_list.html', context)

def filter_orders(orders, selected_master, selected_status):
    if selected_master:
        orders = orders.filter(master_id__in=selected_master)
    if selected_status:
        orders = orders.filter(status__in=selected_status)
    return orders

def handle_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        messages.success(request, "Вы успешно вошли в систему")
        return redirect('order_list')  
    else:
        messages.error(request, "Ошибка. Попробуйте войти снова")
        return redirect('order_list')  
    
def delete_order(request, pk):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=pk)
        order.delete()
        messages.success(request, "Заказ успешно удален")
        return redirect('order_list')  
    else:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')
    
def update_order(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')
    current_order = get_object_or_404(Order, id=pk)
    
    if request.method == "POST":
        form = AddOrderForm(request.POST, instance=current_order)  
        if form.is_valid():
            form.save()  
            messages.success(request, "Заказ обновлен") 
            return redirect('order_list')  
    else:
        form = AddOrderForm(instance=current_order) 
    context = {
        'form': form,
        'order': current_order,
    }
    
    return render(request, 'update_order.html', context)