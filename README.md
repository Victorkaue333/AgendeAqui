# 📅 AgendeAqui - Sistema de Gestão de Espaços Acadêmicos

<div align="center">

![Django](https://img.shields.io/badge/Django-5%2B-darkgreen?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Sistema robusto e intuitivo para agendamento inteligente de salas, laboratórios e espaços acadêmicos**

[Sobre](#sobre) • [Funcionalidades](#-funcionalidades) • [Instalação](#-instalação) • [Uso](#-uso) • [Estrutura](#-estrutura-do-projeto) • [Contribuir](#-contribuindo)

</div>

---

## Sobre

**AgendeAqui** é uma plataforma web desenvolvida em Django que revoluciona a forma como instituições de ensino gerenciam seus espaços físicos. O sistema elimina conflitos de horários, centraliza requisições de reserva e oferece visibilidade total sobre a utilização de recursos. Além disso, o mesmo foi desenvolvido como requisito para conclusão do curso FIC.

Ideal para:
- ✅ Universidades e faculdades
- ✅ Escolas técnicas e institutos  
- ✅ Centros de pesquisa
- ✅ Qualquer instituição com múltiplos espaços compartilhados

---

## ✨ Funcionalidades

### 🔐 Autenticação & Segurança
- Login seguro com controle de sessão
- Recuperação de senha por email
- Controle granular de permissões por função (Admin, Professor, Coordenação, Aluno)
- Auditoria de ações no sistema

### 📍 Gestão de Espaços
- Cadastro completo de salas, laboratórios e auditórios
- Atributos customizáveis (capacidade, recursos disponíveis, horários)
- Marcação de salas como indisponíveis
- Visualização de disponibilidade em tempo real

### 📅 Agendamentos Inteligentes
- Solicitação de reservas com validação automática
- Fluxo de aprovação por coordenadores
- Prevenção inteligente de conflitos de horários
- Suporte a reservas recorrentes
- Histórico completo de todas as requisições

### 📊 Dashboard & Relatórios
- Painel executivo com estatísticas em tempo real
- Gráficos de utilização por espaço e período
- Relatórios customizáveis em PDF/CSV
- Análise de ociosidade de recursos
- Exportação de dados para análise externa

### 🔔 Notificações
- Notificações instantâneas no painel
- Alertas por email para aprovação/rejeição
- Lembretes automáticos de reservas
- Notificação de espaços liberados

### 👥 Gestão de Usuários
- Perfil completo do usuário
- Histórico de agendamentos pessoais
- Alteração de senha e dados cadastrais
- Controle de atividades por período

---

## 💻 Tech Stack

| Camada | Tecnologia | Versão |
|--------|-----------|---------|
| **Backend** | Django | 5.0+ |
| **Linguagem** | Python | 3.10+ |
| **Frontend** | Bootstrap + HTML5/CSS3 | 5.3.0 |
| **Banco de Dados** | SQLite / PostgreSQL | - |
| **Icons** | Font Awesome | 6.4.0 |
| **HTTP Client** | Django Built-in | - |

---

## 🚀 Instalação

### Pré-requisitos
- **Python 3.10 ou superior** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/))
- **pip** (geralmente vem com Python)

### Passo 1: Clone o repositório
```bash
git clone https://github.com/Victorkaue333/AgendeAqui.git
cd AgendeAqui
```

### Passo 2: Crie um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instale as dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configure o banco de dados
```bash
cd administracao
python manage.py migrate
```

### Passo 5: Crie um usuário administrador
```bash
python manage.py createsuperuser
# Siga as instruções na tela
```

### Passo 6: Inicie o servidor
```bash
python manage.py runserver
```

Abra seu navegador e acesse: **http://127.0.0.1:8000**

---

## 📖 Uso

### Primeiro Acesso
1. Acesse a página de login
2. Use as credenciais do superusuário criado
3. Explore o dashboard e configure suas salas

### Para Administradores
1. Acesse `/admin` para gerenciar usuários
2. Cadastre salas em "Salas & Labs"
3. Aprove/rejeite agendamentos no dashboard
4. Gere relatórios em "Relatórios"

### Para Professores
1. Faça login com suas credenciais
2. Solicite reservas em "Agendamentos"
3. Visualize seus agendamentos no calendário
4. Acompanhe status das requisições

### Para Coordenadores
1. Acesse o painel de aprovações
2. Revise todas as solicitações pendentes
3. Aprove ou rejeite com justificativas
4. Gere relatórios de utilização

---

## 📁 Estrutura do Projeto

```
AgendeAqui/
├── administracao/              # App principal (settings, urls, wsgi)
│   ├── settings.py            # Configurações do Django
│   ├── urls.py                # Rotas principais
│   ├── templates/             # Templates globais
│   │   ├── base.html          # Layout base com navbar
│   │   ├── acesso_rapido.html # Dashboard de acesso rápido
│   │   ├── landinpage.html    # Página de landing
│   │   └── login.html         # Página de login
│   └── static/                # Assets estáticos
│       └── css/responsive.css
│
├── agendamentos/              # App para agendamentos
│   ├── models.py              # Modelo de Agendamento
│   ├── views.py               # Lógica de agendamentos
│   ├── urls.py                # Rotas de agendamentos
│   └── templates/agendamentos/
│       └── agendamentos.html
│
├── salas/                     # App para gestão de salas
│   ├── models.py              # Modelo de Sala
│   ├── views.py               # CRUD de salas
│   ├── urls.py                # Rotas de salas
│   └── templates/salas/
│       ├── list.html          # Listagem com modals
│       ├── form.html          # Formulário
│       └── modal_form.html
│
├── dashboard/                 # App do dashboard
│   ├── models.py
│   ├── views.py               # Estatísticas e gráficos
│   └── templates/dashboard.html
│
├── relatorios/                # App de relatórios
│   ├── views.py               # Geração de PDFs/CSVs
│   └── templates/relatorios/
│
├── usuarios/                  # App de perfis de usuário
│   ├── models.py              # Extensão do User model
│   ├── views.py               # Gestão de perfil
│   ├── forms.py               # Formulários de autenticação
│   └── templates/perfil.html
│
├── db.sqlite3                 # Banco de dados (desenvolvimento)
├── manage.py                  # Utilitário Django
├── requirements.txt           # Dependências do projeto
└── README.md                  # Este arquivo
```

---

## 🎨 Interface

O AgendeAqui oferece uma interface moderna e responsiva:

- **Página de Login**: Design limpo com autenticação segura
- **Dashboard Rápido**: Acesso em grid aos principais módulos
- **Landing Page**: Apresentação visual com animações suaves
- **Modalidades**: Formulários inline com validação
- **Temas**: Modo claro com paleta Indigo/Slate

---

## 🔒 Segurança

- ✅ CSRF Protection habilitada
- ✅ SQL Injection prevenido (ORM do Django)
- ✅ XSS Protection em templates
- ✅ Autenticação de sessão segura
- ✅ Permissões granulares por função

---

## 📱 Responsividade

O sistema é totalmente **mobile-first** e funciona perfeitamente em:
- 📱 Smartphones (320px+)
- 📱 Tablets (768px+)
- 🖥️ Desktops (1024px+)

---

## 🐛 Solução de Problemas

### "ModuleNotFoundError: No module named 'django'"
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
python manage.py runserver 8001
```

### Migrações não aplicadas
```bash
python manage.py migrate --run-syncdb
```

### Cache não atualizando
```bash
# Limpar cache do navegador (Ctrl+Shift+Delete)
# Ou forçar reload: Ctrl+F5
```

---

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:
```
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por [Victor Kaue](https://github.com/Victorkaue333)

**Parte do FIC de Desenvolvimento Web com Django**

---

<div align="center">

**Transformando a gestão acadêmica em simples, ágil e eficiente!** 🎓✨

[⬆ Voltar ao topo](#-agendeaqui---sistema-de-gestão-de-espaços-acadêmicos)

</div>
