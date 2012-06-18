from store.models import KeyValue, Parent, KeyValueAdmin, ParentAdmin
from django.contrib import admin

admin.site.register(Parent, ParentAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
