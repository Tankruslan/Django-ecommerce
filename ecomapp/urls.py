from django.urls import path
from ecomapp.views import *
# from django.views.generic import TemplateView

app_name = 'ecomapp'
urlpatterns = [
	path('', base_view, name='base'),
	path('category/<str:category_slug>/', category_view, name='category_detail'),
	path('product/<str:product_slug>/', product_view, name='product_detail'),
	path('add_to_cart/', add_to_cart_view, name='add_to_cart'),
	path('remove_from_cart/', remove_from_cart_view, name='remove_from_cart'),
	path('change_item_quantity/', change_item_quantity_view, name='change_item_quantity'),
	path('cart/', cart_view, name='cart'),
	# path('checkout/', checkout_view, name='checkout'),
	path('order/', order_create_view, name='create_order'),
	path('make_order/', make_order_view, name='make_order'),
	path('thank_you/', thank_you_view, name='thank_you'),
	path('logout/', logout_view, name='logout'),
	path('account/', account_view, name='account'),
]