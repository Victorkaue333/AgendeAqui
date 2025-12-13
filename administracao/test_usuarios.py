#!/usr/bin/env python
"""
Script de teste para validar o sistema de gerenciamento de usuários.
Execução: python test_usuarios.py
"""

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracao.settings')
django.setup()

from django.contrib.auth.models import User
from administracao.models import Perfil, AuditLog
from usuarios.forms import AlterarPerfilForm, CriarUsuarioForm
from usuarios.views import admin_required
import sys

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_models():
    """Testa se os modelos estão configurados corretamente"""
    print_header("TESTE 1: Modelos")
    
    try:
        # Verificar Perfil
        assert hasattr(Perfil, '_meta'), "Perfil model não encontrado"
        assert hasattr(Perfil, 'PERFIL_CHOICES'), "PERFIL_CHOICES não encontrado"
        print("✓ Modelo Perfil validado")
        
        # Verificar AuditLog
        assert hasattr(AuditLog, '_meta'), "AuditLog model não encontrado"
        print("✓ Modelo AuditLog validado")
        
        # Verificar campos
        perfil = Perfil._meta
        assert perfil.get_field('tipo'), "Campo 'tipo' não encontrado"
        print("✓ Campo 'tipo' em Perfil validado")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_forms():
    """Testa se os formulários estão configurados"""
    print_header("TESTE 2: Formulários")
    
    try:
        # Verificar AlterarPerfilForm
        form = AlterarPerfilForm()
        assert 'tipo' in form.fields, "Campo 'tipo' não encontrado em AlterarPerfilForm"
        print("✓ AlterarPerfilForm validado")
        
        # Verificar CriarUsuarioForm
        form = CriarUsuarioForm()
        campos = ['first_name', 'last_name', 'email', 'telefone', 'departamento', 'tipo']
        for campo in campos:
            assert campo in form.fields, f"Campo '{campo}' não encontrado em CriarUsuarioForm"
        print("✓ CriarUsuarioForm validado")
        
        # Teste de validação
        data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@test.com',
            'telefone': '(11) 99999-9999',
            'departamento': 'TI',
            'tipo': 'PRO'
        }
        form = CriarUsuarioForm(data)
        assert form.is_valid(), f"Form inválido: {form.errors}"
        print("✓ Validação de formulário funcionando")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_views():
    """Testa se as views estão configuradas"""
    print_header("TESTE 3: Views")
    
    try:
        from usuarios import views
        
        # Verificar admin_required decorator
        assert hasattr(views, 'admin_required'), "Decorator admin_required não encontrado"
        print("✓ Decorator @admin_required existe")
        
        # Verificar classes/funções
        assert hasattr(views, 'UsuariosListView'), "UsuariosListView não encontrada"
        assert hasattr(views, 'criar_usuario'), "criar_usuario não encontrada"
        assert hasattr(views, 'editar_perfil_usuario'), "editar_perfil_usuario não encontrada"
        assert hasattr(views, 'redefinir_senha_usuario'), "redefinir_senha_usuario não encontrada"
        assert hasattr(views, 'excluir_usuario'), "excluir_usuario não encontrada"
        assert hasattr(views, 'detalhes_usuario'), "detalhes_usuario não encontrada"
        
        print("✓ UsuariosListView validada")
        print("✓ criar_usuario validada")
        print("✓ editar_perfil_usuario validada")
        print("✓ redefinir_senha_usuario validada")
        print("✓ excluir_usuario validada")
        print("✓ detalhes_usuario validada")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_urls():
    """Testa se as URLs estão configuradas"""
    print_header("TESTE 4: URLs")
    
    try:
        from django.urls import reverse
        
        # Testar se as URLs existem
        urls_to_test = [
            ('usuarios:usuarios_list', 'Listagem de usuários'),
            ('usuarios:criar_usuario', 'Criar usuário'),
        ]
        
        for url_name, descricao in urls_to_test:
            url = reverse(url_name)
            print(f"✓ {descricao}: {url}")
        
        return True
    except Exception as e:
        print(f"✗ Erro ao resolver URLs: {e}")
        return False

def test_templates():
    """Verifica se os templates existem"""
    print_header("TESTE 5: Templates")
    
    try:
        from django.template.loader import get_template
        
        templates = [
            'usuarios/usuarios_list.html',
            'usuarios/criar_usuario.html',
            'usuarios/editar_perfil.html',
            'usuarios/redefinir_senha.html',
            'usuarios/excluir_confirm.html',
            'usuarios/detalhes_usuario.html',
        ]
        
        for template_name in templates:
            try:
                get_template(template_name)
                print(f"✓ {template_name} encontrado")
            except Exception as e:
                print(f"✗ {template_name}: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Erro ao verificar templates: {e}")
        return False

def test_database():
    """Testa conexão com banco de dados"""
    print_header("TESTE 6: Banco de Dados")
    
    try:
        # Verificar se tabelas existem
        users_count = User.objects.count()
        perfil_count = Perfil.objects.count()
        audit_count = AuditLog.objects.count()
        
        print(f"✓ Usuários no banco: {users_count}")
        print(f"✓ Perfis no banco: {perfil_count}")
        print(f"✓ Logs de auditoria: {audit_count}")
        
        return True
    except Exception as e:
        print(f"✗ Erro ao acessar banco: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  TESTES DO SISTEMA DE GERENCIAMENTO DE USUÁRIOS          ║")
    print("║  AgendeAqui - Sistema de Agendamento                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Executar testes
    results.append(("Modelos", test_models()))
    results.append(("Formulários", test_forms()))
    results.append(("Views", test_views()))
    results.append(("URLs", test_urls()))
    results.append(("Templates", test_templates()))
    results.append(("Banco de Dados", test_database()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status:12} - {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para usar.")
        return 0
    else:
        print(f"\n❌ {total - passed} teste(s) falharam. Verifique os erros acima.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
