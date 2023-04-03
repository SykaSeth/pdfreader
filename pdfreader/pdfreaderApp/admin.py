from django.contrib import admin
from .models import Invoices, Dishes, DishesProducts, QRCode#, User

admin.site.register(Invoices)
admin.site.register(Dishes)
admin.site.register(DishesProducts)
admin.site.register(QRCode)
# admin.site.register(User)