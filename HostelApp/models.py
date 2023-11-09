from django.db import models
from django.db.models import F

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from account.models import CustomUser


class MealHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meal_history')
    date = models.DateField()
    lunch = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    dinner = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    meal_sum_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Check if it's a new entry
            existing_entry = MealHistory.objects.filter(user=self.user, date=self.date).first()
            if existing_entry:
                # Update the existing entry by adding the new values
                existing_entry.lunch += self.lunch
                existing_entry.dinner += self.dinner
                existing_entry.meal_sum_per_day = existing_entry.lunch + existing_entry.dinner
                existing_entry.save()
                return
        self.meal_sum_per_day = self.lunch + self.dinner
        super(MealHistory, self).save(*args, **kwargs)

    @classmethod
    def get_monthly_total(cls, year, month):
        # Calculate the total meal_sum_per_day for all users in the specified year and month
        total_meal_sum = (
            cls.objects
            .filter(date__year=year, date__month=month)
            .aggregate(total=Sum('meal_sum_per_day'))
        )

        return total_meal_sum#total_meal_sum['total'] or 0
    
class BazarHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='bazar_history')
    date = models.DateField(null=False)
    daily_bazar_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    bazar_details= models.TextField(null=True, blank=True)
