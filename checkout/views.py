from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm

# Create your views here.
def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There are no items in your bag")
        return redirect(reverse('products'))  # This will prevent people from manually accessing the URL by typing /checkout
    
    order_form = OrderForm()  # empty instance of form
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51RZTdpQW7xcmvXE5YuPX1cU4JRDl35zh0AbyIqeFNdo48W1o2KflTqaJtfStbreI9aAA7vZWpvxwID4F5Km3hB5V00n24aUU4w',
        'client_secret': 'test client secret',

    }

    return render(request, template, context)
    