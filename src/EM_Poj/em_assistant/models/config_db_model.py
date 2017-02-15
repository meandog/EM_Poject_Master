from django.db import models


# Static Table of Edgemarc configuration.  This can and only should be changed via the admin console!
class EmConfig(models.Model):
    config_name = models.CharField(max_length=40)
    is_dynamic = models.BooleanField()
    category = models.CharField(max_length=40)
    accepted_value = models.CharField(max_length=40)
    description = models.TextField()
    gui_id = models.IntegerField()
    def __str__(self):
        return 'Config: {}'.format(self.config_name)



