from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Measurement, Master

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Имя'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Фамилия'}))


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'Логин'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Обязательно. Не более 150 символов. Разрешены буквы, цифры и только @/./+/-/_.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Пароль'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"> <li>Ваш пароль не должен быть слишком похож на вашу другую личную информацию.</li><li>Ваш пароль должен содержать как минимум 8 символов.</li><li>Ваш пароль не должен быть распространённым паролем.</li><li>Ваш пароль не может состоять только из цифр.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Введите тот же пароль, что и ранее, для подтверждения.</small></span>'	


class AddMeasurementForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Имя клиента", "class": "form-control"}),
        label=""
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Фамилия клиента", "class": "form-control"}),
        label=""
    )
    phone = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Телефон", "class": "form-control"}),
        label=""
    )
    address = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "Адрес", "class": "form-control"}),
        label=""
    )
    measurement_date = forms.DateTimeField(
        required=True,
        widget=forms.widgets.DateInput(attrs={
            "placeholder": "Дата замера:",
            "class": "form-control",
            "type": "datetime-local" 
        }),
        label="Дата и время замера:"
    )
    master = forms.ModelChoiceField(
        queryset=Master.objects.all(),  
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Мастер:"
    )
    
    status = forms.ChoiceField(
        choices=Measurement.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Статус"  
    )
    measurement_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        label="Файл замера (необязательно)"
    )

    class Meta:
        model = Measurement
        fields = ['first_name', 'last_name', 'phone', 'address', 'measurement_date', 'master', 'status', 'measurement_file']