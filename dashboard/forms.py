from django import forms
from . models import *
from django.contrib.auth.forms import UserCreationForm


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'description']

class DateInput(forms.DateInput):
    input_type = 'date'

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        widgets = {'due': DateInput()}
        fields = ['subject', 'title', 'description', 'due', 'is_finished']

class DashboardForm(forms.Form):
    text = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your search',
            'class': 'form-control rounded-pill-start'
        })
    )

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'is_finished']

class ConversionForm(forms.Form):
    CHOICES = [('length', 'Length'), ('mass', 'Mass')]
    measurement = forms.ChoiceField(
        choices=CHOICES, 
        widget=forms.RadioSelect,
        label='Select Conversion Type'
    )

class ConversionLengthForm(forms.Form):
    CHOICES = [('yard', 'Yard'), ('foot', 'Foot')]
    input = forms.FloatField(
        required=False, 
        label='',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter the number', 
            'step': 'any'
        })
    )
    measure1 = forms.ChoiceField(
        choices=CHOICES, 
        label='From', 
        widget=forms.Select
    )
    measure2 = forms.ChoiceField(
        choices=CHOICES, 
        label='To', 
        widget=forms.Select
    )

class ConversionMassForm(forms.Form):
    CHOICES = [('pound', 'Pound'), ('kilogram', 'Kilogram')]
    input = forms.FloatField(
        required=False, 
        label='',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter the number', 
            'step': 'any'
        })
    )
    measure1 = forms.ChoiceField(
        choices=CHOICES, 
        label='From', 
        widget=forms.Select
    )
    measure2 = forms.ChoiceField(
        choices=CHOICES, 
        label='To', 
        widget=forms.Select
    )

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']