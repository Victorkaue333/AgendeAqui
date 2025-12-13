"""
Testes para o app de agendamentos.
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
from agendamentos.models import Agendamento
from salas.models import Sala, Bloco
from administracao.models import Perfil


@pytest.fixture
def bloco():
    return Bloco.objects.create(nome='Bloco A')


@pytest.fixture
def sala(bloco):
    return Sala.objects.create(
        nome='Sala 101',
        capacidade=30,
        bloco=bloco
    )


@pytest.fixture
def usuario():
    user = User.objects.create_user(
        username='professor1',
        email='professor1@test.com',
        password='senha123'
    )
    Perfil.objects.create(usuario=user, tipo='PRO')
    return user


@pytest.fixture
def coordenador():
    user = User.objects.create_user(
        username='coord1',
        email='coord1@test.com',
        password='senha123'
    )
    Perfil.objects.create(usuario=user, tipo='COO')
    return user


@pytest.mark.django_db
class TestAgendamentoModel:
    """Testes do modelo Agendamento"""
    
    def test_criar_agendamento_valido(self, usuario, sala):
        """Deve criar agendamento com dados válidos"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        agendamento = Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            motivo='Aula de Python',
            status='P'
        )
        
        assert agendamento.id is not None
        assert agendamento.status == 'P'
        assert str(agendamento) == f"#{agendamento.pk} - {sala} em {tomorrow} (08:00:00–10:00:00)"
    
    def test_horario_inicio_maior_que_fim(self, usuario, sala):
        """Deve falhar se horário de início for maior que o fim"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        with pytest.raises(ValidationError):
            agendamento = Agendamento(
                usuario=usuario,
                sala=sala,
                data=tomorrow,
                horario_inicio=time(10, 0),  # Fim antes do início
                horario_fim=time(8, 0),
                motivo='Teste',
                status='P'
            )
            agendamento.full_clean()
    
    def test_conflito_de_horarios_aprovados(self, usuario, sala):
        """Deve detectar conflito com agendamento aprovado existente"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Criar agendamento aprovado
        Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='A'  # Aprovado
        )
        
        # Tentar criar conflitante
        with pytest.raises(ValidationError):
            agendamento = Agendamento(
                usuario=usuario,
                sala=sala,
                data=tomorrow,
                horario_inicio=time(9, 0),  # Conflita
                horario_fim=time(11, 0),
                status='P'
            )
            agendamento.full_clean()
    
    def test_pendente_nao_conflita(self, usuario, sala):
        """Agendamento pendente não deve bloquear outros"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Criar agendamento pendente
        Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='P'  # Pendente
        )
        
        # Outro agendamento no mesmo horário deve ser permitido
        agendamento = Agendamento(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(9, 0),
            horario_fim=time(11, 0),
            status='P'
        )
        agendamento.full_clean()  # Não deve levantar erro
    
    def test_horarios_adjacentes_permitidos(self, usuario, sala):
        """Horários adjacentes devem ser permitidos"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Primeiro agendamento
        Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='A'
        )
        
        # Segundo agendamento (adjacente)
        agendamento = Agendamento(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(10, 0),  # Começa quando o outro termina
            horario_fim=time(12, 0),
            status='P'
        )
        agendamento.full_clean()  # Não deve levantar erro


@pytest.mark.django_db
class TestAgendamentoPermissions:
    """Testes de permissões de agendamentos"""
    
    def test_professor_pode_solicitar(self, usuario, sala):
        """Professor deve poder solicitar agendamento"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        agendamento = Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='P'
        )
        
        assert agendamento.usuario == usuario
        assert agendamento.status == 'P'
    
    def test_coordenador_pode_aprovar(self, coordenador, usuario, sala):
        """Coordenador deve poder aprovar agendamento"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        agendamento = Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='P'
        )
        
        # Aprovar
        agendamento.status = 'A'
        agendamento.save()
        
        assert agendamento.status == 'A'
    
    def test_coordenador_pode_reprovar_com_justificativa(self, coordenador, usuario, sala):
        """Coordenador deve poder reprovar com justificativa"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        agendamento = Agendamento.objects.create(
            usuario=usuario,
            sala=sala,
            data=tomorrow,
            horario_inicio=time(8, 0),
            horario_fim=time(10, 0),
            status='P'
        )
        
        # Reprovar
        agendamento.status = 'R'
        agendamento.justificativa_reprovacao = 'Sala já reservada para outro evento'
        agendamento.save()
        
        assert agendamento.status == 'R'
        assert agendamento.justificativa_reprovacao is not None


@pytest.mark.django_db
class TestSalaModel:
    """Testes do modelo Sala"""
    
    def test_criar_sala(self, bloco):
        """Deve criar sala com sucesso"""
        sala = Sala.objects.create(
            nome='Sala 102',
            capacidade=40,
            bloco=bloco
        )
        
        assert sala.id is not None
        assert sala.nome == 'Sala 102'
        assert sala.capacidade == 40
    
    def test_sala_str_representation(self, bloco):
        """Deve ter representação string correta"""
        sala = Sala.objects.create(
            nome='Sala 103',
            capacidade=30,
            bloco=bloco
        )
        
        assert str(sala) == f"Sala 103 ({bloco.nome})"


@pytest.mark.django_db
class TestPerfilModel:
    """Testes do modelo Perfil"""
    
    def test_perfil_criado_com_usuario(self):
        """Perfil deve ser criado com usuário"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='senha123'
        )
        perfil = Perfil.objects.create(usuario=user, tipo='PRO')
        
        assert perfil.usuario == user
        assert perfil.tipo == 'PRO'
        assert perfil.get_tipo_display() == 'Professor'
    
    def test_tipos_de_perfil(self):
        """Deve suportar todos os tipos de perfil"""
        tipos = ['ADM', 'COO', 'PRO']
        
        for tipo in tipos:
            user = User.objects.create_user(
                username=f'user_{tipo}',
                email=f'{tipo}@test.com',
                password='senha123'
            )
            perfil = Perfil.objects.create(usuario=user, tipo=tipo)
            assert perfil.tipo == tipo
