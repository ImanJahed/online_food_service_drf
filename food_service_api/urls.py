from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.CustomerLoginView.as_view()),
    # ساخت کاربر عادی
    path('create-user/', views.CustomerCreateView.as_view(), name='create-user'),

    # ساخت رستوران
    path('create-restaurant/', views.RestaurantProfileCreateView.as_view(), name='create-restaurant'),

    # لیست رستوران های باز
    path('restaurants/', views.OpenRestaurantsListView.as_view(), name='restaurant_list'),

    # سود شرکت در یک زمان خاص
    path('daily-company-profit/', views.DailyCompanyProfitView.as_view(), name='daily_company_profit'),

    # سود شرکت به ازای هر رستوران
    path('restaurant-total-profit/', views.RestaurantTotalProfitView.as_view(), name='restaurant_total_profit'),

    # سود شرکت در زمان خاص و رستوران خاص
    path('restaurant-income/', views.RestaurantIncomeView.as_view(), name='restaurant_income'),

    # سود شرکت در یک بازه زمانی
    path('company-net-profit/', views.CompanyNetProfitView.as_view(), name='company_net_profit'),

    # درصد تحویل سفارش هر رستوران
    path('restaurant-delivery-percentage/', views.RestaurantDeliveryPercentageView.as_view(), name='restaurant_delivery_percentage'),

    # سود شرکت در یک بازه به ازای
    path('profit-report/', views.ProfitReportView.as_view(), name='profit_report'),

    # ثبت سفارش کاربر
    path('create-order/', views.CreateOrderView.as_view(), name='create_order'),

    # لست غذاهای هر رستوران
    path('restaurant/<int:restaurant_id>/foods/', views.RestaurantFoodListView.as_view(), name='restaurant_food_list'),

    # ساخت منو غذا توسط رستوران
    path('restaurant/<int:restaurant_id>/create_food/', views.CreateFoodView.as_view(), name='create_food'),

    # دریافت سفارش کاربر برای رستوان
    path('user-restaurant-orders/<int:restaurant_id>/', views.UserRestaurantOrdersView.as_view(), name='user_restaurant_orders'),
    # تغییر وضعیت سفارش
    path('change-order-status/<int:order_id>/', views.ChangeOrderStatusView.as_view(), name='change_order_status'),

    # دریافت صورت حساب در روز جاری
    path('daily-restaurant-summary/', views.DailyRestaurantSummaryView.as_view(), name='daily_restaurant_summary'),

    # دریافت صورت حساب در زمان انتخاب شده
    path('restaurant-daily-invoice/<str:date_str>/', views.RestaurantDailyInvoiceView.as_view(), name='restaurant_daily_invoice'),

    # جستجو
    path('search-food/', views.SearchFoodView.as_view(), name='search_food'),

    # جزئیات سفارش کاربر
    path('order-details/<int:order_id>/', views.OrderDetailsView.as_view(), name='order_details'),

    # تغییر وضعیت سفارش
    path('update-order-status/<int:order_id>/', views.OrderStatusUpdateView.as_view(), name='update_order_status'),

    # لغو کردن سفارش بعد گدشت t+10 از زمان آماده سازی غذا
    path('cancel-order/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),
]
