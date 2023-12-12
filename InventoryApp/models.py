from django.db import models
import datetime

# Create your models here.
class Item(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Piece'),
        ('kg', 'KG'),
    ]
    item_name = models.CharField(max_length=200)
    variant = models.CharField(null=False, max_length=100,default='Deshi')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')

    class Meta:
        unique_together = ['item_name', 'variant']

    

    def __str__(self):
        return f"{self.id}: {self.item_name}-{self.variant}"
    
class Invoice(models.Model):
    purchase_date = models.DateField(blank=False)
    product_list = models.JSONField(blank=False)
    Billing_address  = models.TextField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    po_number= models.IntegerField(null=True, blank=True)
    subtotal= models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.id}"
    

class ItemInventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='item_inventory')
    Invoice_no = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='invoice_no',blank=False, default=None)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    damage_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True,default=0)
    purchase_date = models.DateField(null=False)

    def __str__(self):
        return f"{self.item} - {self.quantity}"

    class Meta:
        verbose_name_plural = 'Item Inventories'

    # def save(self, *args, **kwargs):
    #     # If damage_quantity is specified, reduce the quantity accordingly
    #     if self.damage_quantity:
    #         self.quantity -= self.damage_quantity

    #     super().save(*args, **kwargs)


class UsageInventory(models.Model):
    item = models.ForeignKey('Item', on_delete=models.PROTECT, related_name='user_inventory')
    using_date = models.DateField(null=False,default=datetime.date.today)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, null=False)


    def __str__(self):
        return f"{self.item} - {self.quantity_used}"