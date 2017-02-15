from django.db import models

# This is for the tmp table we want to use for the current request.  Will be dumped at end of tasks.
# First class is the EM basic info.
class EmProfileCurrent(models.Model):
    em_name = models.CharField(max_length=40)


# Second class is for the config settings that we want to compare
class EmConfigCurrent(models.Model):
    local_config_name = models.CharField(max_length=40)
