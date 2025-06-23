from django.apps import AppConfig


class CounselorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "counselor"

    def ready(self):
        from django.apps import apps
        from vectordb.shortcuts import autosync_model_to_vectordb

        import counselor.signals

        models = apps.get_app_config("collegecounselor").get_models()

        for model in models:
            autosync_model_to_vectordb(model)
