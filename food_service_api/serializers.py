from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Restaurant, Customer, Food, Order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # تنها در حین ایجاد کاربر نمایش داده می‌شود

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)

    class Meta:
        model = Customer
        fields = ('user', 'address',)

    #     read_only_fields = ('id', 'date_added', 'is_public')
    #
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            customer = Customer.objects.create(user=user, **validated_data)
            return customer
        return None


class RestaurantProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Restaurant
        fields = ('user', 'name', 'restaurant_type', 'start_time', 'finish_time', 'delivery_cost', 'delivery_time')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            restaurant = Restaurant.objects.create(user=user, **validated_data)
            return restaurant
        return None


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id', 'food_name', 'duration', 'price')


class CreateFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('food_name', 'duration', 'price')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user', 'food')


class SearchSerializer(serializers.Serializer):
    q = serializers.CharField()


class RestaurantIdSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField()


class RestaurantDateSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField()
    target_date = serializers.DateField()


class DateProfitSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class TargetDateSerializer(serializers.Serializer):
    target_date = serializers.DateField()
