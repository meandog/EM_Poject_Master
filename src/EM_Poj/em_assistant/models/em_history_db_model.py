from django.db import models

# This model, is how we are storing the all the succesfull Edgemarc tests and the outcome.  We can check for this
# anytime someone does a check, or ask to review history.

class EmConfigHistory(models.Model):
    em_name = models.CharField(max_length=40)
    em_ip_address = models.GenericIPAddressField()
    em_first_seen = models.DateField(auto_now_add=True)