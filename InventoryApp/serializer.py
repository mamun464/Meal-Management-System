from rest_framework import serializers
from .models import Item,ItemInventory,Invoice
from datetime import date


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class InventoryCreateSerializer(serializers.ModelSerializer):
    # item = ItemSerializer()  # Include the related item fields

    class Meta:
        model = ItemInventory
        fields = '__all__'

    def validate_item(self, value):
        # Check if the item exists in the Item model
        try:
            item = Item.objects.get(pk=value.pk)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Selected item does not exist in the Item model.")

        return value

    def validate_purchase_date(self, value):
        # Check if the purchase_date is greater than today's date
        if value > date.today():
            raise serializers.ValidationError("Purchase date cannot be greater than today's date.")

        # Check if the purchase_date is not null
        if value is None:
            raise serializers.ValidationError("Purchase date is required.")

        # Additional validation logic for purchase_date if needed

        return value
            # Check if damage_quantity is greater than quantity


    def validate(self, data):
        # Call the parent validate method first
        validated_data = super().validate(data)
                # Retrieve values for quantity and damage_quantity
        quantity = validated_data.get('quantity')
        damage_quantity = validated_data.get('damage_quantity')

        # Check if damage_quantity is greater than quantity
        if damage_quantity is not None and quantity is not None and damage_quantity > quantity:
            raise serializers.ValidationError("Damage quantity must be less than or equal to quantity.")
        # Additional validation logic if needed

        return validated_data
class InventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer()  # Include the related item fields

    class Meta:
        model = ItemInventory
        fields = '__all__'

    def validate_item(self, value):
        # Check if the item exists in the Item model
        try:
            item = Item.objects.get(pk=value.pk)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Selected item does not exist in the Item model.")

        return value

    def validate_purchase_date(self, value):
        # Check if the purchase_date is greater than today's date
        if value > date.today():
            raise serializers.ValidationError("Purchase date cannot be greater than today's date.")

        # Check if the purchase_date is not null
        if value is None:
            raise serializers.ValidationError("Purchase date is required.")

        # Additional validation logic for purchase_date if needed

        return value
            # Check if damage_quantity is greater than quantity


    def validate(self, data):
        # Call the parent validate method first
        validated_data = super().validate(data)
                # Retrieve values for quantity and damage_quantity
        quantity = validated_data.get('quantity')
        damage_quantity = validated_data.get('damage_quantity')

        # Check if damage_quantity is greater than quantity
        if damage_quantity is not None and quantity is not None and damage_quantity > quantity:
            raise serializers.ValidationError("Damage quantity must be less than or equal to quantity.")
        # Additional validation logic if needed

        return validated_data
    

class InventoryDamageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemInventory
        fields = ['id','damage_quantity']
        
    def validate_damage_quantity(self, value):
        # Get the instance being updated
        instance = self.instance

        # Ensure damage_quantity is not greater than quantity
        if instance and value is not None and value > instance.quantity:
            raise serializers.ValidationError("Damage quantity cannot be greater than quantity.")

        return value

    def update(self, instance, validated_data):
        # Additional validation logic if needed
        
        # Update the fields
        instance.damage_quantity = validated_data.get('damage_quantity', instance.damage_quantity)

        # Save the instance
        instance.save()

        return instance
    
# class VariantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Item
#         fields = ['item_name', 'variant', 'unit']

class SingleInventorySerializer(serializers.ModelSerializer):
    item = ItemSerializer()  # Include the related item fields

    class Meta:
        model = ItemInventory
        fields = '__all__'