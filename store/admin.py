from store.models import KeyValue, Parent
from django.contrib import admin
from treebeard.admin import TreeAdmin


class KeyValueInline(admin.StackedInline):
    model = KeyValue.parent_id.through
    extra = 3

class ParentAdmin(TreeAdmin):
    inlines = [KeyValueInline]

class KeyValueAdmin(admin.ModelAdmin):
    fields = (('key', 'value'),)
    inlines = [KeyValueInline]

admin.site.register(Parent, ParentAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
