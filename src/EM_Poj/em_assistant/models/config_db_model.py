from django.db import models


# Static Table of Edgemarc configuration.  This can and only should be changed via the admin console!
class EmConfig(models.Model):
    config_name = models.CharField(max_length=40, unique=True, null=False, editable=False)
    config_id = models.IntegerField(editable=False, primary_key=True)
    is_dynamic = models.BooleanField()
    category = models.CharField(max_length=40)
    accepted_value = models.CharField(max_length=40)
    description = models.TextField()
    gui_id = models.IntegerField()

    def __str__(self):
        return 'Config: {}'.format(self.config_name)


# Class for history root table storage.
# This has a relationship with EmConfigValueHistory for the em_config_valid_found_ids INT list col
class EmResultHistory(models.Model):
    em_mac_key = models.IntegerField(primary_key=True, unique=True)
    em_name = models.CharField(max_length=40)
    em_ip_address = models.GenericIPAddressField()
    em_first_seen = models.DateTimeField(auto_now_add=True, editable=False)
    em_last_seen = models.DateTimeField(auto_now=True, editable=False)
    em_seen_count = models.IntegerField(default=1, editable=False)

    def __str__(self):
        return 'Config: {}'.format(self.em_mac_key)


# Class for holding all history config values
class EmConfigValueHistory(models.Model):
    em_identifier = models.IntegerField(primary_key=True, unique=True)
    config_name_seen = models.CharField(max_length=40)
    config_value_seen = models.CharField(max_length=40)

    def __str__(self):
        return 'Config: {}'.format(self.em_identifier)
