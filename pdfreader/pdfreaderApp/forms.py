from django import forms
from .models import Invoices, Dishes#, User
from django.contrib.auth.forms import AuthenticationForm

class AddInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoices
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class AddDishForm(forms.ModelForm):
    class Meta:
        model = Dishes
        fields = ['name', 'photo', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class SignUpForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur', max_length=100)
    # , widget=forms.TextInput(attrs={'type': 'text', 'id': 'username'})
    email = forms.EmailField(label='Adresse e-mail', max_length=100)
    last_name = forms.CharField(label='Nom', max_length=100)
    first_name = forms.CharField(label='Prénom', max_length=100)
    password = forms.CharField(label='Mot de passe', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}))

# class LoginForm(forms.Form):
#     email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email', 'class': 'form-control'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
