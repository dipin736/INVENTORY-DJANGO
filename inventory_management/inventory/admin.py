from django.contrib import admin
from .models import Item  
from django.contrib.auth.models import User

# Register the Item model
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'quantity', 'price')
    search_fields = ('name',) 
    list_filter = ('quantity',)
    ordering = ('name',) 

admin.site.register(Item, ItemAdmin)  
admin.site.unregister(User) 
