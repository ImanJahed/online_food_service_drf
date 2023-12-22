from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from datetime import datetime, date, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .models import Restaurant, Food, Order, Customer
from .serializers import RestaurantProfileSerializer, CustomerSerializer, CreateFoodSerializer, FoodSerializer, OrderSerializer, UserSerializer, CustomerLoginSerializer, \
    SearchSerializer, RestaurantIdSerializer, RestaurantDateSerializer, DateProfitSerializer, TargetDateSerializer



class CustomerLoginView(APIView):
    serializer_class = CustomerLoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:

                return Response({'Login'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not active'}, status=400)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)




# ساخت کاربر عادی
class CustomerCreateView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


# ساخت رستوران
class RestaurantProfileCreateView(generics.CreateAPIView):
    serializer_class = RestaurantProfileSerializer


# لیست رستوران های باز
class OpenRestaurantsListView(generics.ListAPIView):
    serializer_class = RestaurantProfileSerializer

    def get_queryset(self):
        current_time = datetime.now().time()
        return Restaurant.objects.filter(start_time__lte=current_time, finish_time__gte=current_time)


# ساخت منو غذا توسط رستوران
class CreateFoodView(APIView):
    serializer_class = CreateFoodSerializer
    def post(self, request, restaurant_id, format=None):
        serializer = CreateFoodSerializer(data=request.data)
        if serializer.is_valid():
            restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
            serializer.save(restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# لست غذاهای هر رستوران
class RestaurantFoodListView(generics.ListAPIView):
    serializer_class = FoodSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # دریافت آیدی رستوران از درخواست
        restaurant_id = self.kwargs['restaurant_id']
        return Food.objects.filter(restaurant_id=restaurant_id)


# ثبت سفارش کاربر
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# سود شرکت در یک زمان خاص
class DailyCompanyProfitView(APIView):
    @extend_schema(
        parameters=[
            TargetDateSerializer,
        ]
    )
    def get(self, request):
        target_date_string = request.query_params.get('target_date', None)

        if target_date_string:
            try:
                target_date = date.fromisoformat(target_date_string)
                total_admin_share = Order.objects.filter(created_at__date=target_date).aggregate(
                    total_admin_share=Sum('total_admin_share')
                )['total_admin_share'] or 0

                return Response({'target_date': target_date, 'total_admin_share': total_admin_share})
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            return Response({'error': 'Please provide a target_date'}, status=400)


# سود شرکت به ازای هر رستوران
class RestaurantTotalProfitView(APIView):
    @extend_schema(
        parameters=[
            RestaurantIdSerializer,
        ]
    )
    def get(self, request):
        restaurant_id = request.query_params.get('restaurant_id', None)

        if restaurant_id:
            restaurant_profit = Order.objects.filter(food__restaurant_id=restaurant_id).aggregate(
                total_restaurant_profit=Sum('restaurant_share_food') + Sum('restaurant_share_delivery')
            )['total_restaurant_profit'] or 0

            return Response({'restaurant_id': restaurant_id, 'restaurant_profit': restaurant_profit})
        else:
            return Response({'error': 'Please provide a restaurant_id'}, status=400)


# سود شرکت در زمان خاص و رستوران خاص
class RestaurantIncomeView(APIView):
    @extend_schema(
        parameters=[
            RestaurantDateSerializer,
        ]
    )
    def get(self, request):
        target_date_string = request.query_params.get('target_date', None)
        restaurant_id = request.query_params.get('restaurant_id', None)

        if target_date_string and restaurant_id:
            try:
                target_date = date.fromisoformat(target_date_string)
                restaurant_income = Order.objects.filter(
                    created_at__date=target_date, food__restaurant_id=restaurant_id
                ).aggregate(
                    total_restaurant_income=Sum('total_restaurant_share')
                )['total_restaurant_income'] or 0

                return Response({'target_date': target_date, 'restaurant_income': restaurant_income})
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            return Response({'error': 'Please provide a target_date and restaurant_id'}, status=400)


# سود شرکت در یک بازه زمانی
class CompanyNetProfitView(APIView):
    @extend_schema(
        parameters=[
            DateProfitSerializer,
        ]
    )
    def get(self, request, format=None):
        start_date_string = request.query_params.get('start_date', None)
        end_date_string = request.query_params.get('end_date', None)

        if start_date_string and end_date_string:
            try:
                start_date = datetime.strptime(start_date_string, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_string, '%Y-%m-%d').date()

                # محاسبه بازه زمانی بین دو تاریخ
                date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

                # محاسبه سود خالص شرکت برای هر روز از بازه زمانی
                net_profit_per_day = []
                for single_date in date_range:
                    daily_net_profit = Order.objects.filter(created_at__date=single_date).aggregate(
                        total_admin_share=Sum('total_admin_share')
                    )['total_admin_share'] or 0
                    net_profit_per_day.append({'date': single_date, 'net_profit': daily_net_profit})

                return Response({'net_profit_per_day': net_profit_per_day})
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            return Response({'error': 'Please provide start_date and end_date'}, status=400)


# درصد تحویل سفارش هر رستوران
class RestaurantDeliveryPercentageView(APIView):
    @extend_schema(
        parameters=[
            RestaurantIdSerializer,
        ]
    )
    def get(self, request):
        restaurant_id = request.query_params.get('restaurant_id', None)

        if restaurant_id:
            total_orders = Order.objects.filter(food__restaurant_id=restaurant_id).count()
            print(total_orders)
            delivered_orders = Order.objects.filter(
                food__restaurant_id=restaurant_id, status='delivered'
            ).count()
            print(delivered_orders)

            if total_orders > 0:
                delivery_percentage = (delivered_orders / total_orders) * 100
                return Response({'restaurant_id': restaurant_id, 'delivery_percentage': delivery_percentage})
            else:
                return Response({'error': 'No orders found for this restaurant'}, status=404)
        else:
            return Response({'error': 'Please provide a restaurant_id'}, status=400)


# سود شرکت در یک بازه به ازای
class ProfitReportView(APIView):
    @extend_schema(
        parameters=[
            DateProfitSerializer,
        ]
    )
    def get(self, request, format=None):
        start_date_string = request.query_params.get('start_date', None)
        end_date_string = request.query_params.get('end_date', None)

        if start_date_string and end_date_string:
            try:
                start_date = datetime.strptime(start_date_string, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_string, '%Y-%m-%d').date()

                date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

                profit_report = []
                for single_date in date_range:
                    daily_food_profit = Order.objects.filter(
                        created_at__date=single_date
                    ).aggregate(
                        total_food_profit=Sum('admin_share_food')
                    )['total_food_profit'] or 0

                    daily_delivery_profit = Order.objects.filter(
                        created_at__date=single_date
                    ).aggregate(
                        total_delivery_profit=Sum('admin_share_delivery')
                    )['total_delivery_profit'] or 0

                    profit_report.append({
                        'date': single_date,
                        'food_profit': daily_food_profit,
                        'delivery_profit': daily_delivery_profit
                    })

                return Response({'profit_report': profit_report})
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            return Response({'error': 'Please provide start_date and end_date'}, status=400)


# دریافت سفارش کاربر برای رستوان
class UserRestaurantOrdersView(APIView):
    def get(self, request, restaurant_id):
        user = request.user  # کاربر فعلی

        # چک کردن اینکه کاربر فعلی کاربر معتبر است

        orders = Order.objects.filter(user=user, food__restaurant_id=restaurant_id)

        order_list = []
        for order in orders:
            order_data = {
                'order_id': order.id,
                'food_name': order.food.name,
                'status': order.status,
                # سایر جزئیات سفارش
            }
            order_list.append(order_data)

        return Response({'orders': order_list}, status=status.HTTP_200_OK)


# تغییر وضعیت سفارش توسط رستوران
class ChangeOrderStatusView(APIView):
    def put(self, request, order_id):
        restaurant_user = request.user  # کاربر رستوران فعلی

        try:
            order = Order.objects.get(id=order_id)

            # چک کردن اینکه کاربر فعلی صاحب سفارش است یا خیر
            if restaurant_user == order.food.restaurant.user:
                new_status = request.data.get('new_status', None)
                if new_status:
                    order.status = new_status
                    order.save()

                    return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Please provide a new status'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You are not authorized to change this order status'}, status=status.HTTP_403_FORBIDDEN)

        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)


# صورتحساب سفارشات روستوران برای روز جاری
class DailyRestaurantSummaryView(APIView):
    def get(self, request, format=None):
        restaurant_user = request.user  # کاربر رستوران فعلی
        today = date.today()

        orders = Order.objects.filter(
            food__restaurant__user=restaurant_user,
            created_at__date=today
        )

        total_orders = orders.count()
        total_cost = orders.aggregate(total_cost=Sum('food__price'))['total_cost'] or 0
        total_restaurant_income = orders.aggregate(total_income=Sum('total_restaurant_share'))['total_income'] or 0

        summary_data = {
            'total_orders': total_orders,
            'total_cost': total_cost,
            'total_restaurant_income': total_restaurant_income
        }

        return Response({'summary': summary_data})


# دریافت صورتحساب در زمان های انتخاب شده
class RestaurantDailyInvoiceView(APIView):
    def get(self, request, date_str, format=None):
        restaurant_user = request.user  # کاربر رستوران فعلی

        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            orders = Order.objects.filter(
                food__restaurant__user=restaurant_user,
                created_at__date=selected_date
            )

            total_orders = orders.count()
            total_cost = orders.aggregate(total_cost=Sum('food__price'))['total_cost'] or 0
            total_restaurant_income = orders.aggregate(total_income=Sum('restaurant_share_food') + Sum('restaurant_share_delivery'))['total_income'] or 0

            invoice_data = {
                'selected_date': selected_date,
                'total_orders': total_orders,
                'total_cost': total_cost,
                'total_restaurant_income': total_restaurant_income
            }

            return Response({'invoice': invoice_data})

        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)


# جستجوی غذا با نام غذا توسط کاربر عادی
class SearchFoodView(APIView):
    @extend_schema(
        parameters=[
            SearchSerializer,
        ]
    )
    def get(self, request):
        search_query = request.query_params.get('q', None)

        if search_query:
            foods = Food.objects.filter(food_name__icontains=search_query)
            serialized_foods = [{'id': food.id, 'name': food.food_name, 'price': food.price} for food in foods]
            return Response({'results': serialized_foods})
        else:
            return Response({'error': 'Please provide a search query'}, status=400)


# جزئیتات سفارش کاربر
class OrderDetailsView(APIView):
    def get(self, request, order_id):
        user = request.user  # کاربر فعلی

        try:
            order = Order.objects.get(id=order_id, user=user)

            order_details = {
                'food_name': order.food.food_name,
                'restaurant_name': order.food.restaurant.name,
                'delivery_time': order.food.restaurant.delivery_time,
                'food_price': order.food.price,
                'order_status': order.status
            }

            return Response({'order_details': order_details})
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)


class OrderStatusUpdateView(APIView):
    def put(self, request, order_id, format=None):
        user = request.user  # کاربر فعلی

        try:
            order = Order.objects.get(id=order_id, user=user)

            # اگر وضعیت فعلی سفارش "در حال آماده‌سازی" نباشد و زمان گذشته، وضعیت را به "در حال آماده‌سازی" تغییر دهید
            if order.status == 'initial' and (timezone.now() - order.created_at).total_seconds() >= 300:
                order.status = 'preparing'
                order.save()

                return Response({'message': 'Order status updated to preparing'}, status=200)
            else:
                return Response({'message': 'Order status remains unchanged'}, status=200)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)


# لغو کردن سفارش بعد گدشت t+10 از زمان آماده سازی غذا
class CancelOrderView(APIView):
    def delete(self, request, order_id, format=None):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            food = order.food

            # چک کردن گذشتن 10 دقیقه از زمان آماده‌سازی غذا
            preparation_time = food.duration  # زمان آماده‌سازی غذا در دقیقه
            if (timezone.now() - order.created_at).total_seconds() >= preparation_time * 60 + 600 and order.status == 'preparing':
                # اگر گذشته بود، سفارش را لغو کنید
                order.status = 'canceled'
                order.save()
                return Response({'message': 'Order has been successfully canceled'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'The order cannot be canceled at this time'}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
