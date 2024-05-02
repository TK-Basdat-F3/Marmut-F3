from django import forms
from .models import CustomUser, CustomLabel

class SignupFormPengguna(forms.ModelForm):
    ROLE_CHOICES = [
        ('podcaster', 'Podcaster'),
        ('artist', 'Artist'),
        ('songwriter', 'Songwriter')
    ]
    
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    nama = forms.CharField(label='Nama')
    gender = forms.ChoiceField(label='Gender', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')])
    tempat_lahir = forms.CharField(label='Tempat Lahir')
    tanggal_lahir = forms.DateField(label='Tanggal Lahir', widget=forms.DateInput(attrs={'type': 'date'}))
    kota_asal = forms.CharField(label='Kota Asal')
    role = forms.MultipleChoiceField(label='Role', widget=forms.CheckboxSelectMultiple, choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'nama', 'gender', 'tempat_lahir', 'tanggal_lahir', 'kota_asal', 'role')

class SignupFormLabel(forms.ModelForm):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    nama = forms.CharField(label='Nama')
    kontak = forms.CharField(label='Kontak')

    class Meta:
        model = CustomLabel
        fields = ('email', 'password', 'nama', 'kontak')
