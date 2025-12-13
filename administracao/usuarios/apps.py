from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        """
        Importar signals quando a aplicação estiver pronta.
        Isso garante que os sinais sejam registrados.
        """
        import usuarios.signals  # noqa: F401
