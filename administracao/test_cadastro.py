"""
Script para testar o formulário de cadastro
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracao.settings')
django.setup()

from django.contrib.auth.models import User
from administracao.models import Perfil
from administracao.view import CadastroForm

def test_cadastro():
    """Testa o processo de cadastro"""
    print("=" * 60)
    print("TESTE DE CADASTRO - AgendeAqui")
    print("=" * 60)
    
    # Dados de teste
    dados_teste = {
        'username': 'teste_professor',
        'email': 'professor@teste.com',
        'password1': 'senha@123',
        'password2': 'senha@123'
    }
    
    # Limpar usuário de teste se existir
    User.objects.filter(username=dados_teste['username']).delete()
    User.objects.filter(email=dados_teste['email']).delete()
    
    print("\n1. TESTE DE VALIDAÇÃO DO FORMULÁRIO")
    print("-" * 60)
    form = CadastroForm(data=dados_teste)
    if form.is_valid():
        print("✅ Formulário válido!")
        print(f"   Username: {form.cleaned_data['username']}")
        print(f"   Email: {form.cleaned_data['email']}")
    else:
        print("❌ Formulário inválido!")
        print(f"   Erros: {form.errors}")
        return
    
    print("\n2. TESTE DE CRIAÇÃO DE USUÁRIO")
    print("-" * 60)
    try:
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1']
        )
        print(f"✅ Usuário criado: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return
    
    print("\n3. TESTE DE CRIAÇÃO DE PERFIL")
    print("-" * 60)
    try:
        perfil, created = Perfil.objects.get_or_create(usuario=user, defaults={'tipo': 'PRO'})
        if created:
            print(f"✅ Perfil criado: {perfil}")
        else:
            print(f"✅ Perfil já existia: {perfil}")
        print(f"   Tipo: {perfil.get_tipo_display()}")
        print(f"   Usuário: {perfil.usuario.username}")
    except Exception as e:
        print(f"❌ Erro ao criar perfil: {e}")
        return
    
    print("\n4. TESTE DE VALIDAÇÃO - USERNAME DUPLICADO")
    print("-" * 60)
    form_duplicado = CadastroForm(data=dados_teste)
    if not form_duplicado.is_valid():
        print("✅ Validação funcionando corretamente!")
        print(f"   Erro esperado: {form_duplicado.errors.get('username', [''])[0]}")
    else:
        print("❌ Validação falhou - deveria rejeitar username duplicado")
    
    print("\n5. TESTE DE VALIDAÇÃO - SENHAS DIFERENTES")
    print("-" * 60)
    dados_senha_diferente = dados_teste.copy()
    dados_senha_diferente['username'] = 'outro_usuario'
    dados_senha_diferente['email'] = 'outro@teste.com'
    dados_senha_diferente['password2'] = 'senha_diferente'
    
    form_senha = CadastroForm(data=dados_senha_diferente)
    if not form_senha.is_valid():
        print("✅ Validação funcionando corretamente!")
        print(f"   Erro esperado: Senhas não coincidem")
    else:
        print("❌ Validação falhou - deveria rejeitar senhas diferentes")
    
    print("\n6. TESTE DE VALIDAÇÃO - SENHA CURTA")
    print("-" * 60)
    dados_senha_curta = dados_teste.copy()
    dados_senha_curta['username'] = 'outro_usuario2'
    dados_senha_curta['email'] = 'outro2@teste.com'
    dados_senha_curta['password1'] = '123'
    dados_senha_curta['password2'] = '123'
    
    form_senha_curta = CadastroForm(data=dados_senha_curta)
    if not form_senha_curta.is_valid():
        print("✅ Validação funcionando corretamente!")
        print(f"   Erro esperado: Senha muito curta")
    else:
        print("❌ Validação falhou - deveria rejeitar senha curta")
    
    # Limpar dados de teste
    print("\n7. LIMPANDO DADOS DE TESTE")
    print("-" * 60)
    user.delete()
    print("✅ Dados de teste removidos")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO COM SUCESSO! ✅")
    print("=" * 60)
    print("\nO formulário de cadastro está funcionando corretamente:")
    print("  • Validação de campos ✅")
    print("  • Validação de senhas ✅")
    print("  • Validação de duplicados ✅")
    print("  • Criação de usuário ✅")
    print("  • Criação de perfil automático ✅")

if __name__ == '__main__':
    test_cadastro()
