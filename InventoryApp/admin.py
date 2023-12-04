from django.contrib import admin
from .models import Item, ItemInventory,UsageInventory

class ItemInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'item','quantity', 'price_per_unit', 'damage_quantity', 'purchase_date')
    search_fields = ('item__item_name', 'item__variant')  # Searching by related Item fields
    list_filter = ( 'item','purchase_date')  # Add filters for unit and purchase date

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'variant','unit')
    search_fields = ('item_name', 'variant')

class UsageInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'item','using_date', 'quantity_used',)
    search_fields = ('item__item_name', 'item__variant')  # Searching by related Item fields

    # def formatted_unit(self, obj):
    #     return f"{obj.item.get_unit_display()}"
    # formatted_unit.short_description = 'Unit'

admin.site.register(UsageInventory, UsageInventoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInventory, ItemInventoryAdmin)
