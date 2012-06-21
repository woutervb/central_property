from store.models import KeyValue, Tree, KeyValueAdmin, TreeAdmin
from django.contrib import admin

admin.site.register(Tree, TreeAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
