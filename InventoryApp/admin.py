from django.contrib import admin
from .models import Item, ItemInventory,UsageInventory,Invoice

class ItemInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'item','quantity', 'price_per_unit', 'damage_quantity', 'purchase_date','Invoice_no')
    search_fields = ('item__item_name', 'item__variant','Invoice_no')  # Searching by related Item fields
    list_filter = ( 'item','purchase_date','Invoice_no')  # Add filters for unit and purchase date

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name', 'variant','unit')
    search_fields = ('item_name', 'variant')

class UsageInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'item','using_date', 'quantity_used',)
    search_fields = ('item__item_name', 'item__variant')  # Searching by related Item fields

    # def formatted_unit(self, obj):
    #     return f"{obj.item.get_unit_display()}"
    # formatted_unit.short_description = 'Unit'

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_date','product_list' ,'Billing_address', 'shipping_address', 'po_number','subtotal')
    search_fields = ['id', 'Billing_address', 'shipping_address', 'po_number']
    list_filter = ('purchase_date',)

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(UsageInventory, UsageInventoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInventory, ItemInventoryAdmin)
