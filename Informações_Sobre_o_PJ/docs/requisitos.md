
## 1. Descrição Geral

O sistema permitirá o agendamento e gerenciamento de salas de aula por parte de professores, coordenadores e administradores, evitando conflitos de horários e otimizando o uso das salas disponíveis na instituição.


## 2. Requisitos

### 2.1 Requisitos Funcionais (RF)

#### Módulo de Autenticação
- RF01: Permitir login e logout de usuários.
- RF02: Suportar perfis de usuário: Administrador, Professor e Coordenação.
- RF03: Permitir cadastro e edição de perfis de usuários (nome, email, senha, cargo, etc).

#### Módulo de Salas
- RF04: Permitir cadastro de salas (nome, número, capacidade, recursos, bloco).
- RF05: Listar todas as salas cadastradas com filtro por bloco, capacidade e recursos.
- RF06: Permitir ao administrador editar ou excluir uma sala.

#### Módulo de Agendamento
- RF07: Permitir ao professor solicitar agendamento de sala em data e horário específicos.
- RF08: Verificar conflitos de horário automaticamente (não permitir reservas sobrepostas).
- RF09: Permitir ao coordenador aprovar ou reprovar solicitações de agendamento.
- RF10: Visualizar agendamentos por dia, semana ou mês (estilo calendário).
- RF11: Permitir cancelar um agendamento antes da data prevista.

#### Módulo de Notificações
- RF12: Notificar por email ou painel sobre aprovação, reprovação ou cancelamento de agendamento.
- RF13: Notificar o professor caso sua solicitação seja rejeitada, informando o motivo.

#### Módulo de Relatórios
- RF14: Gerar relatórios de uso das salas (quantidade de reservas por período, salas mais utilizadas, etc).
- RF15: Permitir exportação de relatórios em PDF ou CSV.


### 2.2 Requisitos Não Funcionais (RNF)

- RNF01: Aplicação desenvolvida em Django 5+.
- RNF02: Banco de dados PostgreSQL.
- RNF03: Front-end com Django Templates + Bootstrap 5.
- RNF04: Sistema responsivo (desktop e mobile).
- RNF05: Permissões gerenciadas via Django Authentication e Groups.

## 3. Telas do Sitema

1️⃣ Tela de Login
Campos: Email, Senha
Botões: “Entrar”, “Esqueci minha senha”

2️⃣ Dashboard (Home)
Exibe um resumo:
Próximos agendamentos do usuário
Status de solicitações (Aprovadas, Pendentes, Reprovadas)
Gráfico rápido de uso de salas (para administradores)

3️⃣ Tela de Salas
Listagem de salas com filtros.
Botão “Cadastrar Nova Sala” (somente para admin).
Campos: Nome da sala, capacidade, bloco, recursos (ex: projetor, ar-condicionado).
Ações: Editar / Excluir.

4️⃣ Tela de Agendamentos
➤ Listagem / Calendário
Visualização estilo calendário semanal com as reservas.
Filtros por sala, data, professor.
➤ Formulário de Solicitação
Campos:
Sala
Data
Horário de início e fim
Motivo da reserva
Botões: “Solicitar Agendamento”, “Cancelar”

➤ Aprovação (Coordenação)
Lista de solicitações pendentes.
Ações: “Aprovar”, “Rejeitar (com motivo)”.

5️⃣ Tela de Relatórios
Filtros:
Período (data inicial / final)
Sala específica
Professor
Gráficos e tabelas de uso
Botões: “Exportar PDF” / “Exportar CSV”

6️⃣ Tela de Perfil do Usuário
Dados pessoais (nome, email, cargo).
Alterar senha.
Histórico de agendamentos realizados.