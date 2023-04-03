from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.files.images import ImageFile
import datetime
import uuid
import os
from .functions import generate_unique_code

# Create your models here.

class Suppliers(models.Model):
    name        =   models.CharField(max_length=255)
    website     =   models.CharField(max_length=255, blank=True)
    description =   models.CharField(max_length=255, blank=True)
    date        =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    class Meta:
        db_table = "suppliers"

    def __str__(self):
        return self.name

class Invoices(models.Model):
    supplier    =   models.ForeignKey(Suppliers, on_delete=models.CASCADE, blank=True, null=True)
    shipping_date = models.DateField(blank=True, default=datetime.date.today)
    code        =   models.CharField(max_length=50, unique=True)
    name        =   models.CharField(max_length = 255)
    file        =   models.FileField(db_column='path', upload_to = 'invoices')
    date        =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    
    class Meta:
        db_table = "invoices"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = generate_unique_code()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

class Products(models.Model):
    invoice =   models.ForeignKey(Invoices, on_delete=models.CASCADE)
    name    =   models.CharField(max_length=255)
    date    =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name

class Dishes(models.Model):
    name        =   models.CharField(max_length=255)
    description =   models.TextField(max_length=1000, blank=True, default='')
    photo       =   models.ImageField(upload_to='dishes', blank=True, default='dishes/food.jpg', max_length=100)
    copy_of    =   models.ForeignKey('self', null="True", blank=True, on_delete=models.SET_NULL)
    date        =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    class Meta:
        db_table = "dishes"
        ordering = ('-date',)

    def __str__(self):
        return self.name

    def duplicate(self):
        """ Crée une copie du plat avec ses relations avec les autres modèles """
        # Création d'une copie du plat original
        dish_copy = Dishes.objects.create(name=self.name, description=self.description, copy_of=self)

        # Copie de la photo
        if self.photo:
            old_path = self.photo.path
            file_ext = os.path.splitext(old_path)[1]
            new_filename = f"{uuid.uuid4()}{file_ext}"
            new_path = os.path.join('dishes', new_filename)
            with open(old_path, 'rb') as old_file:
                dish_copy.photo.save(new_path, ImageFile(old_file))

        # Récupération des produits liés au plat original
        dp = DishesProducts.objects.filter(dish=self)
        for item in dp:
            item.pk = None
            item.dish = dish_copy
            item.save()

        # Retour de la copie du plat
        return dish_copy


    def delete(self, *args, **kwargs):
        if self.photo != 'dishes/food.jpg':
            self.photo.delete()
        super().delete(*args, **kwargs)

class DishesProducts(models.Model):
    dish    =   models.ForeignKey(Dishes, on_delete=models.CASCADE)
    product =   models.ForeignKey(Products, on_delete=models.CASCADE)
    date    =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    class Meta:
        db_table = "dishes_products"

class QRCode(models.Model):
    dish    =   models.ForeignKey(Dishes, on_delete=models.CASCADE)
    link    =   models.CharField(max_length=255)
    path    =   models.ImageField(max_length=255)
    date    =   models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    class Meta:
        db_table = "qr_code"
        ordering = ('-date',)

    def delete(self, *args, **kwargs):
        os.remove(settings.MEDIA_ROOT+'/'+self.path)
        super().delete(*args, **kwargs)
        


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        user = self.model(email=self.normalize_email(email), username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, password=None):
        user = self.create_user(email, username, first_name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = ['username', 'email']
    REQUIRED_FIELDS = ['email', 'username', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin