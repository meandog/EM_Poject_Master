
# This file is used to perform database interaction functions.
# TODO: function for accessing the ~3 DBs for read or write

from .models.config_db_model import EmConfig


class GetValidConfs(object):

    def __init__(self):
        all_items = EmConfig.objects.all()

