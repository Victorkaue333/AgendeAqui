from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from administracao.models import Perfil


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Seu usuário',
                'id': 'id_username',
                'autofocus': 'autofocus',
                'autocomplete': 'username'
            }
        )
    )

    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Sua senha',
                'id': 'id_password',
                'autocomplete': 'current-password'
            }
        )
    )


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Seu usuário',
                'id': 'id_username',
                'autofocus': 'autofocus',
                'autocomplete': 'username'
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com',
                'id': 'id_email',
                'autocomplete': 'email'
            }
        )
    )

    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '********',
                'id': 'id_password1',
                'autocomplete': 'new-password'
            }
        )
    )

    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '********',
                'id': 'id_password2',
                'autocomplete': 'new-password'
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('E-mail já cadastrado.')
        return email


# ============================================================================
# NOVOS FORMULÁRIOS PARA GERENCIAMENTO DE USUÁRIOS
# ============================================================================

class AlterarPerfilForm(forms.ModelForm):
    """Form para alterar o tipo/perfil do usuário"""
    class Meta:
        model = Perfil
        fields = ['tipo']
        widgets = {
            'tipo': forms.RadioSelect(choices=Perfil.PERFIL_CHOICES),
        }


class CriarUsuarioForm(forms.Form):
    """Form para criar novo usuário (admin)"""
    first_name = forms.CharField(
        max_length=100,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100,
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=20,
        label='Telefone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 98765-4321'})
    )
    departamento = forms.CharField(
        max_length=100,
        label='Departamento',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        label='Tipo de Usuário',
        choices=Perfil.PERFIL_CHOICES,
        initial='PRO',
        widget=forms.RadioSelect()
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

