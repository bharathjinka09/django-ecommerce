from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder
from .filters import ProductFilter
from .forms import CustomerForm


def store(request):

    filtered_products = ProductFilter(
        request.GET,
        queryset=Product.objects.all()
    )

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()

    offer_messages = Offer.objects.all()

    paginated_filtered_products = Paginator(filtered_products.qs, 3)
    page_number = request.GET.get('page')
    product_page_obj = paginated_filtered_products.get_page(page_number)

    # messages.success(request, 'Item added to cart')

    context = {'product_page_obj': product_page_obj,
               'filtered_products': filtered_products,
               'products': products,
               'offer_messages': offer_messages,
               'cartItems': cartItems,
               }

    return render(request, 'store/store.html', context)


def logout_user(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems': cartItems}

    return render(request, 'store/logout_user.html', context)


def product_detail(request, id):
    data = cartData(request)
    cartItems = data['cartItems']

    product = get_object_or_404(Product, pk=id)

    # messages.success(request, 'Item added to cart')

    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)


@login_required(login_url='/accounts/google/login/?process=login')
def get_user_profile(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    shipping_address = ShippingAddress.objects.filter(id=request.user.id)
    customer_orders = OrderItem.objects.filter(id=request.user.id)
    order_status = Order.objects.filter(id=request.user.id)

    context = {'items': items, 'order': order, 'order_status': order_status,
               'cartItems': cartItems, 'customer_orders': customer_orders,
               'form': form, 'shipping_address': shipping_address}

    return render(request, 'store/user_profile.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    print(data)
    productId = data['productId']
    action = data['action']

    print('Action', action)
    print('productId', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse("Payment Complete!", safe=False)


# from allauth.account.views import SignupView, LoginView, LogoutView

# class MyLogoutView(LogoutView):
#     template_name = 'store/logout_user.html'

# class MySignupView(SignupView):
#     template_name = 'my_signup.html'


# class MyLoginView(LoginView):
#     template_name = 'my_login.html'
