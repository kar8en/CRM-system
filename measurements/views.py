from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddMeasurementForm
from .models import Measurement, Master


def home(request):
    masters = Master.objects.all()
    measurements = Measurement.objects.all()

    # Получаем выбранные значения из GET-запроса
    selected_master = request.GET.get('master', '')
    selected_status = request.GET.getlist('status')  # Используем getlist для получения всех выбранных статусов

    # Фильтрация замеров по выбранным мастерам и статусам
    if selected_master:
        measurements = measurements.filter(master_id=selected_master)

    if selected_status:
        measurements = measurements.filter(status__in=selected_status)

    context = {
        'measurements': measurements,
        'masters': masters,
        'selected_master': selected_master,
        'selected_status': selected_status,  # Передаем выбранные статусы
        'STATUS_CHOICES': Measurement.STATUS_CHOICES,  # Передаем доступные статусы
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
	form = AddMeasurementForm(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if form.is_valid():
				add_measurement = form.save()
				messages.success(request, "Замер добавлен")
				return redirect('home')
		return render(request, 'add_measurement.html', {'form':form})
	else:
		messages.success(request, "Необходимо войти в систему")
		return redirect('home')


def update_measurement(request, pk):
	if request.user.is_authenticated:
		current_measurement = Measurement.objects.get(id=pk)
		form = AddMeasurementForm(request.POST or None, instance=current_measurement)
		if form.is_valid():
			form.save()
			messages.success(request, "Замер обновлен")
			return redirect('home')
		return render(request, 'update_measurement.html', {'form':form})
	else:
		messages.success(request, "Необходимо войти в систему")
		return redirect('home')
