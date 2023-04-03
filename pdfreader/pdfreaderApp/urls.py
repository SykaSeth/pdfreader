from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home, name="home"),

    path('invoice', views.invoices, name="invoices"),
    path('invoice/<str:code>/', views.invoice, name="invoice"),
    path('invoice/add', views.add_invoice, name="add_invoice"),
    path('delete_invoice/<int:id>/', views.delete_invoice, name="delete_invoice"),

    path('product', views.products, name="products"),
    path('product/search', views.search_product, name="search_product"),

    path('dish', views.dishes, name="dishes"),
    path('dish/<int:id>/', views.dish, name="dish"),
    path('dish/add', views.add_dish, name="add_dish"),
    path('dish/update/<int:id>/', views.update_dish, name="update_dish"),
    path('dish/duplicate/<int:id>/', views.duplicate_dish, name="duplicate_dish"),
    path('delete_dish/<int:id>/', views.delete_dish, name="delete_dish"),
    path('dish/pdf/<int:id>/', views.dish_pdf, name="dish_pdf"),

    path('qrcode', views.qr_codes, name="qr_codes"),
    path('qrcode/<int:id>/', views.qr_code, name="qr_code"),

    # path('user/log', views.login_view, name="login_view"),
    # path('user/signup', views.signup, name="signup"),
    # path('user/logout', views.logout_view, name="logout_view"),

    path('user', views.user, name="user"),
    path('user/login', views.login, name="login"),
    path('user/logout', views.logout, name="logout"),
    path('user/register', views.register, name="register"),
    path('user/details', views.user_details, name="user_details"),
    path('user/update', views.update_user, name="update_user"),
    path('user/delete', views.delete_user, name="delete_user"),

    # path('user/admin', views.admin, name="admin"),
    # path('user/admin/users', views.admin_users, name="admin_users"),

]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)