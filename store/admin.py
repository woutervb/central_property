from store.models import KeyValue, Tree
from django.contrib import admin
from treebeard.admin import TreeAdmin


class KeyValueInline(admin.StackedInline):
    model = KeyValue.tree_id.through
    extra = 3

#class ParentAdmin(admin.ModelAdmin):
#    change_list_template = 'admin/tree_change_list.html'
class ParentAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    change_list_template = 'admin/tree_change.html'
    inlines = [KeyValueInline]

class KeyValueAdmin(admin.ModelAdmin):
    fields = (('key', 'value'),)
    inlines = [KeyValueInline]

admin.site.register(Tree, TreeAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
