from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json

# Create your views here.

@require_POST
def cache_checkout_data(request):
    """before we call the confirm card payment method in the stripe javascript, we make a post request
    to this view and give it the client secret from the payment intent, split it at the word secret to get the id
    then add metadata to it to get the save info by the user
    """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    
    except Exception as e:
        messages.error(request, 'Your payment could not be processed, try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # I'm doing this manually in order to skip the save infobox which doesn't have a field on the order model.
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # create instance of form
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save(commit=False)  # commit=False prevents first save to happen in database??

            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()

            # And then we need to iterate through the bag items to create each line item.
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # Finally this should theoretically never happen but just in case a product isn't found we'll add an error message.
                # Delete the empty order and return the user to the shopping bag page.
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            request.session['save_info'] = 'save-info' in request.POST
            print(order.order_number)
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
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
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        # print(intent)        
        order_form = OrderForm()  # empty instance of form

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                            Is it set in your environment?')


        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,

        }

        return render(request, template, context)
    

def checkout_success(request, order_number):
    """Handle sucessful checkouts"""
    print(order_number)

    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    
    # delete bag from session
    if 'bag' in request.session:
        del request.session['bag']
    
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
