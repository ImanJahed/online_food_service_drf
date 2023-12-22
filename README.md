# Online Food Service Api

# **سرویس سفارش آنلاین غذا**


# نحوه اجرای پروژه

1- ساخت محیط مجازی با دستور:

`python -m venv venv`

2-نصب نیازمندهای پروژه

`pip install -r requirements.txt`

3- ساخت دیتابیس

`python manage.py migrate`

4- ساخت ادمین

`python manage.py createsuperuser`

5-اجرای پروژه

_`python manage.py runserver`_
 
6- تست api

http://127.0.0.1:8000/docs/

پ.ن: هرجایی که نیاز به احراز هویت بود از سوپر یوزر ساخته شده استفاده شود