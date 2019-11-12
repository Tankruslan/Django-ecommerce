from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils.text import slugify
from transliterate import translit
from django.contrib.auth.models import User
# from decimal import Decimal
# from django.conf import settings
from django.utils import timezone
from PIL import Image


# Create your models here.

def one_day_hence():
    return timezone.now() + timezone.timedelta(days=1)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse('ecomapp:category_detail', kwargs={'category_slug': self.slug})


def pre_save_category_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify(translit(instance.name, reversed=True))
        instance.slug = slug


pre_save.connect(pre_save_category_slug, sender=Category)


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def image_folder(instance, filename):
    filename = instance.product.slug + '.' + filename.split('.')[1]
    return "{0}/{1}".format(instance.product.slug, filename)


class Product(models.Model):
    category = models.ForeignKey(Category, null=True, default=None,
                                 on_delete=models.SET_NULL)
    configuration = models.CharField(max_length=100, null=True, default=None)
    discount = models.IntegerField(default=0, blank=True, null=True,
                                   verbose_name='Discount, %')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return "Товар: %s ; Цена: %s" % (self.title, self.price)

    def get_absolute_url(self):
        return reverse('ecomapp:product_detail', kwargs={'product_slug': self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-images')
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        super(ProductImage, self).save(*args, *kwargs)

        img = Image.open(self.image.path)

        if img.height > 768 or img.width > 1024:
            resize = (768, 1024)
            img.thumbnail(resize)
            img.save(self.image.path)


class CartItem(models.Model):
    session_key = models.CharField(max_length=128, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(null=True, default=1)
    item_cost = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    all_items_cost = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Создан')

    def __str__(self):
        return str(self.product.title) + ' ' + str(self.quantity) + ' шт. в корзине'

    def save(self, *args, **kwargs):
        item_cost = self.product.price
        self.item_cost = item_cost
        self.all_items_cost = item_cost * int(self.quantity)

        super(CartItem, self).save(*args, **kwargs)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total_cost = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.id)


ORDER_STATUS_CHOICES = (
    ("Принят в обработку", "Принят в обработку"),
    ("Выполняется", "Выполняется"),
    ("Оплачен", "Оплачен")
)

BUYING_TYPE_CHOICES = (
    ('Доставка', 'Доставка'),
    ('Самовывоз', 'Самовывоз')
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=15)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    buying_type = models.CharField(max_length=40, choices=BUYING_TYPE_CHOICES,
                                   default='Доставка')
    address = models.CharField(max_length=250, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_delivery = models.DateTimeField(default=one_day_hence)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES,
                              default='Принят в обработку')

    def __str__(self):
        return ("Заказ №{0}".format(str(self.id)))


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    item_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    all_items_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return "Товар %s" % self.product.title

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def save(self, *args, **kwargs):
        item_cost = self.product.price
        self.item_cost = item_cost
        self.all_items_cost = item_cost * int(self.quantity)

        super(ProductInOrder, self).save(*args, **kwargs)


def product_in_order_post_save(sender, instance, created, **kwargs):
    order = instance.order
    all_products_in_order = ProductInOrder.objects.filter(order=order)

    order_total_price = 0
    for item in all_products_in_order:
        order_total_price += item.all_items_cost

    instance.order.total = order_total_price
    instance.order.save(force_update=True)


post_save.connect(product_in_order_post_save, sender=ProductInOrder)

