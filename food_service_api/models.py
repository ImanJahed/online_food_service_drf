from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Restaurant(models.Model):
    RESTAURANT_TYPES = (
        ('fast_food', 'فست فود'),
        ('traditional', 'سنتی'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # نام رستوران
    restaurant_type = models.CharField(max_length=20, choices=RESTAURANT_TYPES)  # نوع رستوران
    start_time = models.TimeField()  # ساعت کاری
    finish_time = models.TimeField()
    delivery_cost = models.FloatField()  # هزینه حمل
    delivery_time = models.IntegerField()  # مدت زمان حمل به دقیقه

    def __str__(self):
        return self.name


class Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)  # رابطه با مدل رستوران
    food_name = models.CharField(max_length=100)  # نام غذا
    duration = models.IntegerField()  # مدت زمان (به عنوان مثال به دقیقه)
    price = models.FloatField()  # قیمت

    def __str__(self):
        return self.food_name


class Order(models.Model):
    STATUS_CHOICE = (
        ('initial', 'initial'),
        ('preparing', 'preparing'),
        ('delivered', 'delivered'),
        ('canceled', 'canceled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    status = models.CharField(max_length=11, choices=STATUS_CHOICE)

    admin_share_delivery = models.FloatField()
    admin_share_food = models.FloatField()
    total_admin_share = models.FloatField()

    restaurant_share_delivery = models.FloatField(blank=True, null=True)
    restaurant_share_food = models.FloatField()
    total_restaurant_share = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.food:
            self.admin_share_delivery = self.food.restaurant.delivery_cost * 0.2
            self.admin_share_food = self.food.price * 0.04
            self.total_admin_share = self.admin_share_food + self.admin_share_delivery

            self.restaurant_share_food = self.food.price * 0.96
            self.restaurant_share_delivery = self.food.restaurant.delivery_cost * 0.8
            self.total_restaurant_share = self.restaurant_share_food + self.restaurant_share_delivery

        super().save(*args, **kwargs)

    def total_profit(self):
        return self.total_admin_share

    def __str__(self):
        return f'{self.user.username} - {self.food.food_name}'
