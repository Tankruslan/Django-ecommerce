from django.contrib import admin
from ecomapp.models import *
# Register your models here.

class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 0


class ProductInOrderInline(admin.TabularInline):
	model = ProductInOrder
	extra = 0



class CategoryAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in Category._meta.fields]
	list_display = [field.name for field in Category._meta.fields]
	class Meta:
		model = Category
# Register your models here.
admin.site.register(Category, CategoryAdmin)


class BrandAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in Brand._meta.fields]
	list_display = [field.name for field in Brand._meta.fields]
	class Meta:
		model = Brand
# Register your models here.
admin.site.register(Brand, BrandAdmin)


class ProductAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in Product._meta.fields]
	list_display = [field.name for field in Product._meta.fields]
	inlines = [ProductImageInline]
	class Meta:
		model = Product
# Register your models here.
admin.site.register(Product, ProductAdmin)


class ProductImageAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in ProductImage._meta.fields]
	list_display = [field.name for field in ProductImage._meta.fields]
	class Meta:
		model = ProductImage
# Register your models here.
admin.site.register(ProductImage, ProductImageAdmin)


class CartItemAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in CartItem._meta.fields]
	list_display = [field.name for field in CartItem._meta.fields]
	class Meta:
		model = CartItem
# Register your models here.
admin.site.register(CartItem, CartItemAdmin)


class CartAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in Cart._meta.fields]
	list_display = [field.name for field in Cart._meta.fields]
	class Meta:
		model = Cart
# Register your models here.
admin.site.register(Cart, CartAdmin)


class OrderAdmin(admin.ModelAdmin):
	# exclude = ['items']
	list_display_links = [field.name for field in Order._meta.fields]
	list_display = [field.name for field in Order._meta.fields]
	inlines = [ProductInOrderInline]
	class Meta:
		model = Order
# Register your models here.
admin.site.register(Order, OrderAdmin)


class ProductInOrderAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in ProductInOrder._meta.fields]
	list_display = [field.name for field in ProductInOrder._meta.fields]
	class Meta:
		model = ProductInOrder
# Register your models here.
admin.site.register(ProductInOrder, ProductInOrderAdmin)
