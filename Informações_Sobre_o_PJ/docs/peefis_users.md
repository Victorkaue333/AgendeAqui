# 👥 Perfis de Usuários - AgendeAqui

## Visão Geral

O sistema AgendeAqui possui **3 perfis de usuários principais**, cada um com responsabilidades e permissões específicas. Todos os usuários herdam as características básicas de um "Usuário Comum" (autenticação, alteração de senha, etc.), mas com permissões diferenciadas.

---

## 👨‍🏫 1. Professor

### Função Principal
**Solicitar o uso de salas**

### O que faz:
- ✅ Consulta o calendário para visualizar salas disponíveis
- ✅ Solicita reserva de sala em data e horário específicos
- ✅ Recebe notificações sobre aprovação/reprovação de pedidos
- ✅ Visualiza apenas seus agendamentos aprovados
- ✅ Visualiza histórico de solicitações

### Permissões (ACL)
- `view_approved_agendamentos` - Visualizar agendamentos aprovados
- `create_agendamento` - Solicitar novo agendamento
- `view_own_agendamentos` - Visualizar seus próprios agendamentos
- `view_own_profile` - Visualizar seu perfil
- `change_own_password` - Alterar sua própria senha

### Telas Acessíveis
- Dashboard (resumo pessoal)
- Agendamentos (visualizar aprovados + solicitar novo)
- Perfil (dados pessoais + histórico)

### Tipo de Perfil (BD)
```
Perfil.tipo = 'PRO'  # Professor
```

---

## 👩‍💼 2. Coordenador (Coordenação)

### Função Principal
**Moderação e aprovação de solicitações**

### O que faz:
- ✅ Analisa pedidos de agendamento enviados pelos professores
- ✅ Aprova ou reprova solicitações com justificativa
- ✅ Visualiza TODOS os agendamentos (aprovados, pendentes, reprovados)
- ✅ Consulta relatórios de uso das salas
- ✅ Acessa dashboard com estatísticas de agendamentos

### Permissões (ACL)
- `view_all_agendamentos` - Visualizar todos os agendamentos
- `approve_agendamento` - Aprovar/rejeitar solicitações
- `view_pending_agendamentos` - Visualizar agendamentos pendentes
- `view_statistics` - Acessar estatísticas e gráficos
- `view_relatorios` - Gerar e visualizar relatórios básicos
- `view_all_profiles` - Visualizar perfis de usuários
- `view_own_profile` - Visualizar seu perfil
- `change_own_password` - Alterar sua própria senha

### Telas Acessíveis
- Dashboard (estatísticas gerais)
- Agendamentos (visualizar todos + aprovar/reprovar)
- Relatórios (básicos)
- Perfil (dados pessoais)

### Tipo de Perfil (BD)
```
Perfil.tipo = 'COO'  # Coordenador
```

---

## 🛠️ 3. Administrador (Admin)

### Função Principal
**Gestão técnica e infraestrutura**

### O que faz:
- ✅ Cadastra e gerencia salas (criar, editar, excluir)
- ✅ Cadastra blocos e recursos (projetores, AR, computadores, etc.)
- ✅ Cria contas de novos usuários (padrão = Professor)
- ✅ Concede/revoga permissões (promover Professor → Coordenador ou Admin)
- ✅ Visualiza TODOS os agendamentos
- ✅ Acessa todos os relatórios completos
- ✅ Gerencia a infraestrutura do sistema (salas, recursos, etc.)

### Permissões (ACL)
- `manage_users` - Criar, editar e excluir usuários
- `change_user_role` - Alterar perfil/tipo de usuário
- `manage_salas` - Cadastrar, editar e excluir salas
- `manage_blocos` - Cadastrar e gerenciar blocos
- `manage_recursos` - Cadastrar e gerenciar recursos
- `view_all_agendamentos` - Visualizar todos os agendamentos
- `approve_agendamento` - Aprovar/rejeitar agendamentos (backup)
- `view_all_relatorios` - Gerar relatórios completos
- `export_relatorios` - Exportar relatórios (PDF, CSV)
- `view_system_logs` - Acessar logs do sistema
- `view_all_profiles` - Visualizar todos os perfis
- `view_own_profile` - Visualizar seu perfil
- `change_own_password` - Alterar sua própria senha
- `change_any_password` - Redefinir senha de outros usuários

### Telas Acessíveis
- Dashboard (completo com todas as estatísticas)
- Usuários (NOVA - gerenciar usuários e suas permissões)
- Salas (criar, editar, excluir)
- Agendamentos (visualizar todos com todas as ações)
- Relatórios (completos com exportação)
- Perfil (dados pessoais)

### Tipo de Perfil (BD)
```
Perfil.tipo = 'ADM'  # Administrador
```

---

## 🔄 Fluxo de Criação de Novos Usuários

### Processo Padrão:
1. **Admin cria novo usuário** via tela de "Usuários"
2. **Novo usuário recebe email** com credenciais temporárias
3. **Novo usuário faz login** e altera a senha
4. **Novo usuário começa como Professor** (tipo = 'PRO')
5. **Admin pode promover** para Coordenador ou Admin conforme necessário

### Hierarquia de Permissões:
```
Professor (PRO)
    ↓ (promovido por Admin)
Coordenador (COO)
    ↓ (promovido por Admin)
Administrador (ADM)
```

---

## 📋 Resumo Comparativo

| Funcionalidade | Professor | Coordenador | Admin |
|---|---|---|---|
| **Solicitar Agendamento** | ✅ | ✅ | ✅ |
| **Visualizar Próprios Agendamentos** | ✅ | ✅ | ✅ |
| **Visualizar Todos Agendamentos** | ❌ | ✅ | ✅ |
| **Aprovar/Reprovar Agendamentos** | ❌ | ✅ | ✅ |
| **Gerenciar Salas** | ❌ | ❌ | ✅ |
| **Gerenciar Usuários** | ❌ | ❌ | ✅ |
| **Alterar Perfil de Usuário** | ❌ | ❌ | ✅ |
| **Gerar Relatórios** | ❌ | ✅ (Básicos) | ✅ (Completos) |
| **Exportar Relatórios** | ❌ | ❌ | ✅ |
| **Acessar Dashboard** | ✅ (Pessoal) | ✅ (Geral) | ✅ (Completo) |

---

## 🎯 Implementação no Django

### Model Perfil (administracao/models.py)
```python
class Perfil(models.Model):
    TIPO_CHOICES = [
        ('PRO', 'Professor'),
        ('COO', 'Coordenador'),
        ('ADM', 'Administrador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, default='PRO')
    telefone = models.CharField(max_length=20, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.get_tipo_display()})"
    
    def is_professor(self):
        return self.tipo == 'PRO'
    
    def is_coordenador(self):
        return self.tipo == 'COO'
    
    def is_admin(self):
        return self.tipo == 'ADM'
```

### Verificação de Permissões em Views
```python
# Decorator para verificar perfil
def coordenador_required(func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'perfil') or request.user.perfil.tipo not in ['COO', 'ADM']:
            messages.error(request, 'Acesso negado.')
            return redirect('acesso_rapido')
        return func(request, *args, **kwargs)
    return wrapper

# Ou Mixin para Class-Based Views
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.perfil.tipo == 'ADM'
```

---

## 📌 Tela de Usuários (A Implementar)

### Funcionalidade Principal:
- **Listar todos os usuários** com filtro por tipo
- **Promover/Degradar usuário**:
  - Professor → Coordenador
  - Coordenador → Professor ou Admin
  - Admin → Coordenador ou Professor
- **Excluir usuário** (apenas Admin)
- **Redefinir senha** de outro usuário (apenas Admin)
- **Visualizar histórico** de mudanças de perfil

### Campos a Exibir:
- Nome completo
- Email
- Tipo de Perfil (com dropdown para alterar)
- Departamento
- Data de Criação
- Últimas Ações (alterar perfil, última vez logado, etc.)

### Ações Disponíveis:
- 🔄 Alterar Perfil
- 🔑 Redefinir Senha
- 🗑️ Excluir Usuário
- 👁️ Visualizar Detalhes

