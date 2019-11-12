from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import *
from users.models import Profile
from users.forms import ProfileImage
from .forms import *
from .forms import OrderForm
from decimal import Decimal
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from ecomapp.extras import generate_order_id
from django.utils import timezone
# Create your views here.

@login_required
def getting_or_creating_cart(request):
	try:
		cart_id = request.session['cart_id']
		cart = Cart.objects.get(id=cart_id)
		request.session['total'] = cart.items.count()
	except:
		cart = Cart()
		cart.save()
		cart_id = cart.id
		request.session['cart_id'] = cart_id
		cart = Cart.objects.get(id=cart_id)
	return cart

def base_view(request):
	search_query = request.GET.get('search', '')

	if search_query:
		products = Product.objects.filter(title__icontains=search_query, available=True)
	else:
		products = Product.objects.filter(available=True)

	products_in_slider = Product.objects.filter(available=True)
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()
	cart_product_form = CartAddProductForm()
	# paginator = Paginator(products, 1)
	# page = request.GET.get('page')
	# products = paginator.get_page(page)
	context = {
		'cart' : cart,
		'categories': categories,
		'products': products,
		'products_in_slider': products_in_slider,
		'cart_product_form': cart_product_form,
	}
	return render(request, 'ecomapp/index.html', context)

def product_view(request, product_slug):
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()
	product = Product.objects.get(slug=product_slug)
	cart_product_form = CartAddProductForm()
	product_images = ProductImage.objects.filter(is_active=True, product__available=True, 
													product__slug=product_slug)

	context = {
		'cart' : cart,
		'categories' : categories,
		'product' : product,
		'product_images': product_images,
		'cart_product_form': cart_product_form,
	}
	return render(request, 'ecomapp/product.html', context)

def category_view(request, category_slug):
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()	
	category = Category.objects.get(slug=category_slug)
	products_of_category = Product.objects.filter(category=category, available=True)
	cart_product_form = CartAddProductForm()
	paginator = Paginator(products_of_category, 9)
	page = request.GET.get('page')
	products_of_category = paginator.get_page(page)

	context = {
		'cart' : cart,
		'categories' : categories,
		'category' : category,
		'products_of_category' : products_of_category,
		'cart_product_form': cart_product_form,
	}
	return render(request, 'ecomapp/category.html', context)

def cart_view(request):
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()

	context = {
		'cart' : cart,
		'categories' : categories,
	}
	return render(request, 'ecomapp/cart.html', context)


@login_required
def add_to_cart_view(request):
	cart = getting_or_creating_cart(request)
	session_key = request.session.session_key
	if not session_key:
		request.session.cycle_key()
	product_slug = request.POST.get('product_slug')
	product = Product.objects.get(slug=product_slug)

	if request.method == "POST":
		form = CartAddProductForm(request.POST or None)
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
			new_item, created = CartItem.objects.get_or_create(product=product,
				session_key=session_key, defaults={"quantity":quantity})
			if not created:
				new_item.quantity += quantity
				new_item.all_items_cost = product.price*quantity
				new_item.save()
				cart.save()

			if new_item not in cart.items.all():
				cart.items.add(new_item)
				cart.save()

	new_cart_total = 0.00

	for item in cart.items.all():
		new_cart_total += float(item.all_items_cost)
	cart.cart_total_cost = new_cart_total
	cart.save()

	return JsonResponse({
		'cart_total': cart.items.count()
		})

@login_required
def remove_from_cart_view(request):
	cart = getting_or_creating_cart(request)
	product_slug = request.GET.get('product_slug')
	product = Product.objects.get(slug=product_slug)

	for cart_item in cart.items.all():
		if cart_item.product == product:
			cart_item.delete()
			cart.save()

	new_cart_total = 0.00

	for item in cart.items.all():
		new_cart_total += float(item.all_items_cost)

	cart.cart_total_cost = new_cart_total
	cart.save()
	return JsonResponse({
		'cart_total': cart.items.count(),
		'cart_total_price': cart.cart_total_cost,
		})

@login_required
def change_item_quantity_view(request):
	cart = getting_or_creating_cart(request)
	quantity = request.GET.get('quantity')
	item_id = request.GET.get('item_id')
	cart_item = CartItem.objects.get(id=int(item_id))
	cart_item.quantity = int(quantity)
	cart_item.all_items_cost = int(quantity) * Decimal(cart_item.item_cost)
	cart_item.save()

	new_cart_total = 0.00

	for item in cart.items.all():
		new_cart_total += float(item.all_items_cost)

	cart.cart_total_cost = new_cart_total
	cart.save()

	return JsonResponse({
		'cart_total': cart.items.count(),
		'all_items_cost': cart_item.all_items_cost,
		'cart_total_price': cart.cart_total_cost,
		})

# @login_required
# def checkout_view(request):
# 	cart = getting_or_creating_cart(request)
# 	categories = Category.objects.all()
# 	context = {
# 		'cart': cart,
# 		'categories' : categories, 
# 	}
# 	return render(request, 'checkout.html', context)

@login_required
def order_create_view(request):
	cart = getting_or_creating_cart(request)
	form = OrderForm(request.POST or None)
	categories = Category.objects.all()

	context = {
		'cart': cart,
		'form': form,
		'categories' : categories,
	}
	return render(request, 'ecomapp/order.html', context)

@login_required
def make_order_view(request):
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()
	session_key = request.session.session_key
	products_in_cart = CartItem.objects.filter(session_key=session_key)

	if request.method == "POST":
		form = OrderForm(request.POST)

		if form.is_valid():
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			phone = form.cleaned_data['phone']
			buying_type = form.cleaned_data['buying_type']
			address = form.cleaned_data['address']
			date_delivery = form.cleaned_data['date_delivery']
			comments = form.cleaned_data['comments']
			new_order = Order.objects.create(
				user=request.user,
				total=cart.cart_total_cost,
				first_name=first_name,
				last_name=last_name,
				phone=phone,
				address=address,
				buying_type=buying_type,
				comments=comments,
				date_delivery=date_delivery,
				ref_code=generate_order_id()
				)

			for product_in_cart in products_in_cart:
				product_to_order = product_in_cart.product
				quantity_to_order = product_in_cart.quantity
				item_cost_to_order = product_in_cart.item_cost
				all_items_cost_to_order = product_in_cart.all_items_cost

				ProductInOrder.objects.create(
					order=new_order,
					product=product_to_order,
					quantity=quantity_to_order,
					item_cost=item_cost_to_order,
					all_items_cost=all_items_cost_to_order,
					)
			# del request.session['cart_id']
			del request.session['total']
			cart.delete()
			products_in_cart.filter(session_key=session_key).delete()
			return HttpResponseRedirect(reverse('ecomapp:thank_you'))
	else:
		form = OrderForm()
	context = {
		'categories': categories,
		'cart': cart,
		'products_in_cart': products_in_cart,
	}
	return render(request, 'ecomapp/order.html', context)

def thank_you_view(request):
	cart = getting_or_creating_cart(request)
	categories = Category.objects.all()

	context = {
		'categories': categories,
		'cart': cart,
	}
	return render(request, 'ecomapp/thank_you.html', context)

def logout_view(request):
	logout(request)
	messages.success(request, 'Вы успешно вышли.')
	return HttpResponseRedirect("/")

@login_required
def account_view(request):
	order = Order.objects.filter(user=request.user).order_by('-id')
	products_in_order = ProductInOrder.objects.filter()
	categories = Category.objects.all()
	
	instance = get_object_or_404(Profile, user=request.user)
	if request.method == 'POST':	
		image_profile = ProfileImage(request.POST, request.FILES, instance=instance)

		if image_profile.is_valid():
			avatar = image_profile.save(commit=False)
			avatar.user = request.user
			avatar.save()
			messages.success(request, 
				f'Ваш аватар был успешно обновлен!')
			return redirect('ecomapp:account')
	else:
		image_profile = ProfileImage()
	context = {
		'image_profile': image_profile,
		'order': order,
		'products_in_order': products_in_order,
		'categories': categories,
		'instance': instance,
	}

	return render(request, 'ecomapp/account.html', context)
	