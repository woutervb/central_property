from store.models import KeyValue, Parent
from django.contrib import admin
from treebeard.admin import TreeAdmin

class ParentTreeAdmin(TreeAdmin):
    pass

admin.site.register(Parent, ParentTreeAdmin)
admin.site.register(KeyValue)
