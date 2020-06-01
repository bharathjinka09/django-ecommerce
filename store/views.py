from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder
from .filters import ProductFilter
from .forms import CustomerForm
# Create your views here.


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    # product = Product.objects.get(id=id)

    products = Product.objects.all()
    page = request.GET.get('page', 1)

    offer_messages = Offer.objects.all()

    products_list = Product.objects.all()
    paginator = Paginator(products_list, 3)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Filter products
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs

    context = {'products': products,
               'offer_messages': offer_messages,
               'products_page': products_page,
               'cartItems': cartItems, 'myFilter': myFilter}
    return render(request, 'store/store.html', context)

def logout_user(request):

    return render(request, 'store/logout_user.html')


def product_detail(request, id):
    data = cartData(request)
    cartItems = data['cartItems']

    product = get_object_or_404(Product, pk=id)

    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)

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

    context = {'items': items, 'order': order,
               'cartItems': cartItems,
               'form': form}

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


# from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
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
