from django.contrib import admin

# Register your models here.
from .models.config_db_model import EmConfig
from .models.em_history_db_model import EmConfigHistory

admin.site.register(EmConfig)
admin.site.register(EmConfigHistory)