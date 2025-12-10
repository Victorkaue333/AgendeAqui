from django.shortcuts import render

def acesso_rapido(request):
	usuario = request.user if request.user.is_authenticated else None
	# Se first_name estiver vazio, usa username
	user_display_name = usuario.first_name.strip() if usuario and usuario.first_name else (usuario.username if usuario else '')
	context = {
		'usuario': usuario,
		'user_display_name': user_display_name,
	}
	return render(request, 'acesso_rapido.html', context)

def landinpage(request):
	usuario = request.user if request.user.is_authenticated else None
	# Se first_name estiver vazio, usa username
	user_display_name = usuario.first_name.strip() if usuario and usuario.first_name else (usuario.username if usuario else '')
	context = {
		'usuario': usuario,
		'is_authenticated': request.user.is_authenticated,
		'user_display_name': user_display_name,
	}
	return render(request, 'landinpage.html', context)

def login_view(request):
	return render(request, 'login.html')

def cadastro(request):
	return render(request, 'cadastro.html')
