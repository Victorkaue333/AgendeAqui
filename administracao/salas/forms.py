from django import forms
from .models import Sala, Bloco, Recurso


class SalaForm(forms.ModelForm):
    """Formulário customizado para criação/edição de salas"""
    
    # Campo de bloco simplificado
    bloco_nome = forms.ChoiceField(
        choices=[
            ('Bloco Principal', 'Bloco Principal'),
            ('Bloco A', 'Bloco A'),
            ('Bloco B', 'Bloco B'),
            ('Bloco C', 'Bloco C'),
            ('Bloco D', 'Bloco D'),
        ],
        label='Bloco',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Campo de recursos como texto
    recursos_text = forms.CharField(
        required=False,
        label='Recursos Disponíveis',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ex: Projetor, Ar Condicionado, Computadores'
        }),
        help_text='Separe os recursos por vírgula'
    )
    
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sala 101'
            }),
            'capacidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Ex: 30'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se está editando, carregar os valores
        if self.instance and self.instance.pk:
            self.fields['bloco_nome'].initial = self.instance.bloco.nome if self.instance.bloco else ''
            recursos_existentes = self.instance.recursos.all()
            if recursos_existentes:
                self.fields['recursos_text'].initial = ', '.join([r.nome for r in recursos_existentes])
    
    def save(self, commit=True):
        sala = super().save(commit=False)
        
        # Criar ou obter o bloco
        bloco_nome = self.cleaned_data.get('bloco_nome')
        bloco, _ = Bloco.objects.get_or_create(nome=bloco_nome)
        sala.bloco = bloco
        
        if commit:
            sala.save()
            
            # Processar recursos
            recursos_text = self.cleaned_data.get('recursos_text', '')
            if recursos_text:
                # Limpar recursos antigos
                sala.recursos.clear()
                
                # Criar novos recursos
                recursos_lista = [r.strip() for r in recursos_text.split(',') if r.strip()]
                for recurso_nome in recursos_lista:
                    recurso, _ = Recurso.objects.get_or_create(nome=recurso_nome)
                    sala.recursos.add(recurso)
        
        return sala
