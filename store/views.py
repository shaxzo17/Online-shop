from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Category, Product, Order, OrderItem
from .forms import CheckoutForm
from datetime import datetime
from django.http import HttpResponse



def home_view(request):
    return render(request, 'store/home.html')

def category_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    query = request.GET.get('q')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    context = {
        'categories': categories,
        'products': products,
        'query': query,
    }
    return render(request, 'store/category_list.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_detail.html', context)

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(category_id=category_id)
        selected_category = get_object_or_404(Category, id=category_id)
    else:
        selected_category = None

    context = {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product = get_object_or_404(Product, id=product_id)

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart

    messages.success(request, f"{product.name} savatchaga qo‘shildi.")
    
    return redirect(request.META.get('HTTP_REFERER', 'store:categories'))

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart_detail.html', context)


@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
        product = get_object_or_404(Product, id=product_id)
        if quantity > product.stock:
            messages.error(request, f"{product.name} uchun {quantity} dona zaxirada mavjud emas.")
        elif quantity > 0:
            cart[str(product_id)] = quantity
        else:
            cart.pop(str(product_id), None)
    except (ValueError, TypeError):
        messages.error(request, "Noto‘g‘ri miqdor kiritildi.")

    request.session['cart'] = cart
    return redirect('store:cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    messages.success(request, "Mahsulot savatdan o‘chirildi.")
    return redirect('store:cart_detail')


def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        payment = request.POST.get('payment')

        if payment == 'naqd':
            return render(request, 'store/order_success_display.html', {
                'name':first_name,
                'last_name': last_name,
                'phone': phone,
                'address': address,
            })
        elif payment == 'plastik':
            return render(request, 'store/payment_success.html')
        else:
            return HttpResponse("To‘lov turi noto‘g‘ri tanlangan.")
    return render(request, 'store/checkout.html')

def order_confirmation(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Savat bo‘sh.")
        return redirect('store:cart_detail')

    if request.method == 'POST':
        form_data = request.session.get('checkout_data', {})
        address = form_data.get('address')
        payment_method = form_data.get('payment_method')

        if not (address and payment_method):
            messages.error(request, "Manzil va to‘lov usulini kiriting.")
            return render(request, 'store/order_confirmation.html', {'form': CheckoutForm(form_data)})

        order = Order.objects.create(
            address=address,
            payment_method=payment_method,
            created_at=datetime.now()
        )

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            if product.stock < quantity:
                messages.error(request, f"{product.name} uchun yetarli zaxira yo‘q.")
                return redirect('store:cart_detail')
            product.stock -= quantity
            product.save()
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

        request.session['cart'] = {}
        request.session['order_data'] = {
            'name': form_data.get('name'),
            'phone': form_data.get('phone'),
            'address': address,
            'payment_method': payment_method,
            'order_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages.success(request, "Buyurtma muvaffaqiyatli rasmiylashtirildi.")
        return redirect('store:order_success')  # URL nomi bilan

    return render(request, 'store/order_confirmation.html', {'form': CheckoutForm()})

from django.shortcuts import render
from datetime import datetime

def order_success(request):
    context = {
        'order_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'checkout_data': {
            'name': 'Nilufar',
            'phone': '+998885191150',
            'address': 'gulxaniy 22',
        }
    }
    return render(request, 'store/order_success.html', context)
