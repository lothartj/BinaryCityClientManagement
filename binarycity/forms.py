from django import forms
from .models import Client, Contact

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['client_code'] = forms.CharField(
                disabled=True,
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.initial['client_code'] = self.instance.client_code

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name.strip()) < 1:
            raise forms.ValidationError("Name cannot be empty.")
        if len(name) > 255:
            raise forms.ValidationError("Name is too long (maximum 255 characters).")
        return name.strip()

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'surname', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter surname'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("First name is required.")
        if len(name.strip()) < 1:
            raise forms.ValidationError("First name cannot be empty.")
        if len(name) > 255:
            raise forms.ValidationError("First name is too long (maximum 255 characters).")
        return name.strip()

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if not surname:
            raise forms.ValidationError("Surname is required.")
        if len(surname.strip()) < 1:
            raise forms.ValidationError("Surname cannot be empty.")
        if len(surname) > 255:
            raise forms.ValidationError("Surname is too long (maximum 255 characters).")
        return surname.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email address is required.")
        email = email.lower().strip()
        if Contact.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        email = cleaned_data.get('email')
        
        if name and surname and email:
            pass
        
        return cleaned_data 