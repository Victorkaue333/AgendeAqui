from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django import forms
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Perfil


class CadastroForm(forms.Form):
	username = forms.CharField(
		max_length=150,
		required=True,
		widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_username'})
	)
	email = forms.EmailField(
		required=True,
		widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'})
	)
	password1 = forms.CharField(
		required=True,
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password1'})
	)
	password2 = forms.CharField(
		required=True,
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password2'})
	)

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError('Este nome de usuário já está em uso.')
		return username

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('Este e-mail já está cadastrado.')
		return email

	def clean(self):
		cleaned_data = super().clean()
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError('As senhas não coincidem.')

		if password1 and len(password1) < 8:
			raise forms.ValidationError('A senha deve ter no mínimo 8 caracteres.')

		return cleaned_data


def acesso_rapido(request):
	usuario = request.user if request.user.is_authenticated else None
	# Se first_name estiver vazio, usa username
	user_display_name = usuario.first_name.strip() if usuario and usuario.first_name else (usuario.username if usuario else '')
	context = {
		'usuario': usuario,
		'user_display_name': user_display_name,
	}
	return render(request, 'acesso_rapido.html', context)

def landingpage(request):
	usuario = request.user if request.user.is_authenticated else None
	# Se first_name estiver vazio, usa username
	user_display_name = usuario.first_name.strip() if usuario and usuario.first_name else (usuario.username if usuario else '')
	context = {
		'usuario': usuario,
		'is_authenticated': request.user.is_authenticated,
		'user_display_name': user_display_name,
	}
	return render(request, 'landingpage.html', context)

def login_view(request):
	return render(request, 'login.html')

def cadastro(request):
	if request.method == 'POST':
		form = CadastroForm(request.POST)
		if form.is_valid():
			try:
				# Criar o usuário (o perfil será criado automaticamente pelo signal)
				user = User.objects.create_user(
					username=form.cleaned_data['username'],
					email=form.cleaned_data['email'],
					password=form.cleaned_data['password1']
				)
				
				# Se for requisição AJAX, retorna JSON
				if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
					return JsonResponse({
						'success': True,
						'message': 'Cadastro realizado com sucesso!',
						'username': form.cleaned_data['username'],
						'email': form.cleaned_data['email']
					})
				
				messages.success(request, 'Cadastro realizado com sucesso! Faça login para acessar o sistema.')
				return redirect('login')
			except Exception as e:
				if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
					return JsonResponse({
						'success': False,
						'message': f'Erro ao criar usuário: {str(e)}'
					})
				messages.error(request, f'Erro ao criar usuário: {str(e)}')
		else:
			# Se houver erros de validação e for AJAX
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				errors = {}
				for field, error_list in form.errors.items():
					errors[field] = error_list[0]
				return JsonResponse({
					'success': False,
					'errors': errors
				})
	else:
		form = CadastroForm()
	
	return render(request, 'cadastro.html', {'form': form})

def logout_view(request):
	"""View customizada de logout que aceita GET e POST, redirecionando para landing page"""
	logout(request)
	return HttpResponseRedirect(reverse('landingpage'))
