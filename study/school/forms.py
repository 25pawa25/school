from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import Textarea
from django.http import JsonResponse

from .models import *


class AddCourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['title', 'slug', 'intro', 'description', 'cost', 'paid']


class RegisterUserForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = PhoneNumberField()

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone',)


class CodeForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = CustomUser
        fields = ('password',)

class MessageForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Напишите ваше сообщение',
            'rows': 4,
            'cols': 50
        }))

    class Meta:
        model = Message
        fields = ['content']


def message_form(request):
        first_name = request.POST.get.user.first_name#('first_name', '').strip()
        print(f'---------------->{first_name}')
        last_name = request.POST.get.user.last_name#('last_name', '').strip()
        phone = request.POST.get.user.phone#('phone', '').strip()
        message = request.POST.get('message', '').strip()
        if message == '':
            return JsonResponse({'error': 'error'})
        form = Message()
        form.reciever = request.POST.get.user
        form.first_name = first_name
        form.last_name = last_name
        form.message = message
        form.phone = phone
        form.save()
        return JsonResponse({'error': 'success'})


