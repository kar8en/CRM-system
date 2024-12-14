from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddMeasurementForm, AddOrderForm
from .models import Measurement, Master, Order


def home(request):
    masters = Master.objects.all()
    measurements = Measurement.objects.all()

    selected_master = request.GET.getlist('master')
    selected_status = request.GET.getlist('status')

    if selected_master:
        measurements = measurements.filter(master_id__in=selected_master)

    if selected_status:
        measurements = measurements.filter(status__in=selected_status)
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
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

def delete_measurement(request, pk):
	if request.user.is_authenticated:
		delete_it = Measurement.objects.get(id=pk)
		delete_it.delete()
		messages.success(request, "Замер успешно удален")
		return redirect('home')
	else:
		messages.success(request, "Необходимо войти в систему")
		return redirect('home')


def add_measurement(request):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')

    if request.method == "POST":
        form = AddMeasurementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Замер добавлен")
            return redirect('home')
    else:
        form = AddMeasurementForm()

    return render(request, 'add_measurement.html', {'form': form})

def update_measurement(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Необходимо войти в систему")
        return redirect('home')

    current_measurement = get_object_or_404(Measurement, id=pk)
    if request.method == "POST":
        form = AddMeasurementForm(request.POST, request.FILES, instance=current_measurement)
        if form.is_valid():
            form.save()
            messages.success(request, "Замер обновлен")
            return redirect('home')
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
            return redirect('home')  
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