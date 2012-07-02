from store.models import KeyValue, Tree
from django.contrib import admin
from forms import MoveNodeForm

class TreeAdmin(admin.ModelAdmin):
    "Django Admin class for treebeard"
    change_list_template = 'admin/tree_change_list.html'
    form = MoveNodeForm

    def queryset(self, request):
        from treebeard.al_tree import AL_Node
        if issubclass(self.model, AL_Node):
            # AL Trees return a list instead of a QuerySet for .get_tree()
            # So we're returning the regular .queryset cause we will use
            # the old admin
            return super(TreeAdmin, self).queryset(request)
        else:
            return self.model.get_tree()

class KeyValueInline(admin.StackedInline):
    model = KeyValue.tree_id.through
    extra = 3

class KeyValueAdmin(admin.ModelAdmin):
    fields = (('key', 'value'),)
    inlines = [KeyValueInline]

admin.site.register(Tree, TreeAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
