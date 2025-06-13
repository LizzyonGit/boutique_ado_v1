from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe

# Create your views here.
def checkout(request):

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There are no items in your bag")
        return redirect(reverse('products'))  # This will prevent people from manually accessing the URL by typing /checkout
    
    """
    At the top I'm going to import
    the bag contents function from bag.context. Which as you know makes that function
    available for use here in our views. Since really all that function returns
    is a Python dictionary. We can pass it the request
    and get the same dictionary here in the view. I'll store that in a variable called current bag.
    Making sure not to overwrite the bag variable that already exists
    And now to get the total all I need to do is get the grand_total key out of the current bag.
    I'll multiply that by a hundred and round it to zero decimal places using the round function.
    Since stripe will require the amount to charge as an integer.
    """
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount= stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )
    # print(intent)
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
                         Is it set in your environment?')

    order_form = OrderForm()  # empty instance of form
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,

    }

    return render(request, template, context)
    