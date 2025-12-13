from django import forms
from .models import Agendamento


class AgendamentoCreateForm(forms.ModelForm):
    """
    Formulário para criar/solicitar um novo agendamento.
    Usado por Professores para solicitar uma reserva de sala.
    """
    class Meta:
        model = Agendamento
        fields = ['sala', 'data', 'horario_inicio', 'horario_fim', 'motivo']
        widgets = {
            'sala': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'placeholder': 'Selecione a sala'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'date',
                'placeholder': 'Data da reserva'
            }),
            'horario_inicio': forms.TimeInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'time',
                'placeholder': 'Horário de início'
            }),
            'horario_fim': forms.TimeInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'time',
                'placeholder': 'Horário de término'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'rows': 3,
                'placeholder': 'Motivo da reserva (ex: Aula teórica, Laboratório, Seminário)',
                'maxlength': '500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Melhorar rótulos
        self.fields['sala'].label = 'Sala'
        self.fields['data'].label = 'Data da Reserva'
        self.fields['horario_inicio'].label = 'Horário de Início'
        self.fields['horario_fim'].label = 'Horário de Término'
        self.fields['motivo'].label = 'Motivo da Solicitação'

        # Adicionar ajuda nos campos
        self.fields['data'].help_text = 'Selecione a data em que deseja usar a sala'
        self.fields['horario_inicio'].help_text = 'Horário de início (ex: 08:00)'
        self.fields['horario_fim'].help_text = 'Horário de término (ex: 10:00)'

    def clean(self):
        cleaned_data = super().clean()
        horario_inicio = cleaned_data.get('horario_inicio')
        horario_fim = cleaned_data.get('horario_fim')

        if horario_inicio and horario_fim:
            if horario_inicio >= horario_fim:
                raise forms.ValidationError(
                    'O horário de fim deve ser posterior ao horário de início.'
                )
        
        return cleaned_data


class AgendamentoApprovalForm(forms.ModelForm):
    """
    Formulário para Coordenadores aprovarem ou reprovarem agendamentos.
    """
    acao = forms.ChoiceField(
        choices=[
            ('A', 'Aprovar'),
            ('R', 'Reprovar')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Decisão'
    )

    class Meta:
        model = Agendamento
        fields = ['status', 'justificativa_reprovacao']
        widgets = {
            'status': forms.HiddenInput(),
            'justificativa_reprovacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Motivo da recusa (obrigatório se reprovar)',
                'maxlength': '500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['justificativa_reprovacao'].label = 'Justificativa (se reprovar)'
        self.fields['justificativa_reprovacao'].required = False

    def clean(self):
        cleaned_data = super().clean()
        acao = self.cleaned_data.get('acao')
        justificativa = cleaned_data.get('justificativa_reprovacao')

        if acao == 'R' and not justificativa:
            raise forms.ValidationError(
                'Justificativa é obrigatória ao reprovar um agendamento.'
            )

        # Atualizar status baseado na ação
        if acao == 'A':
            cleaned_data['status'] = 'A'
            cleaned_data['justificativa_reprovacao'] = ''
        elif acao == 'R':
            cleaned_data['status'] = 'R'

        return cleaned_data
