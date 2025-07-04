from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):  # it takes in the request and the id of the product the user wants to add
    """add a quantity of the product to the bag """
    # get the product
    product = get_object_or_404(Product, pk=item_id)

    quantity = int(request.POST.get('quantity'))  # get qty from form, convert to integer as it is a string from the form
    redirect_url = request.POST.get('redirect_url')  # get the redirect URL from the form so we know where to redirect once the process here is finished.
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']


    # variable bag accesses the requests session.
    # Trying to get this variable if it already exists. (get('bag'))
    # And initializing it to an empty dictionary if it doesn't. (get(, {}))
    # In this way, we first check to see if there's a bag variable in the session.
    # And if not we'll create one.
    bag = request.session.get('bag', {})

    if size:
        if item_id in list(bag.keys()):
            """
            If the item is already in the bag.
            Then we need to check if another item of the same id and same size already exists.
            And if so increment the quantity for that size and otherwise just set it equal to the quantity.
            Since the item already exists in the bag. But this is a new size for that item.
            """
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'You have successfully updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            # bag[item_id]['items_by_size'][size] drills down to quantity in items by size dictionary
                

            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'You have successfully added size {size.upper()} {product.name}')
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}  # if item id is not already in bag, added like this in case of same item different sizes
            messages.success(request, f'You have successfully added size {size.upper()} {product.name}')
    else:
        # And finally we'll add the item to the bag or update the quantity if it already exists.
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag[item_id] = quantity
            messages.success(request, f'You have successfully added {product.name}')

    # And then overwrite the variable in the session with the updated version.
    request.session['bag'] = bag

    # print(request.session['bag'])  prints to the console to test bag content

    return redirect(redirect_url)  # redirect user back to redirect url

def adjust_bag(request, item_id):  # it takes in the request and the id of the product the user wants to add
    """adjust the quantity of the specified product to the specified amount """
    product = get_object_or_404(Product, pk=item_id)


    quantity = int(request.POST.get('quantity'))  # get qty from form, convert to integer as it is a string from the form
    # we don't need redirect url because we always want to redirect to bag page
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']


    # variable bag accesses the requests session.
    # Trying to get this variable if it already exists. (get('bag'))
    # And initializing it to an empty dictionary if it doesn't. (get(, {}))
    # In this way, we first check to see if there's a bag variable in the session.
    # And if not we'll create one.
    bag = request.session.get('bag', {})

    if size:
        """
        If there's a size. Of course we'll need to drill into the
        items by size dictionary, find that specific size and either set its
        quantity to the updated one or remove it if the quantity submitted is zero.
        """
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'You have successfully updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')

        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
                messages.success(request, f'Removed {size.upper()} {product.name} from bag')

    else:
        """If there's no size that logic is quite simple and we can remove the item
        entirely by using the pop function."""
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')

        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from bag')


    # And then overwrite the variable in the session with the updated version.
    request.session['bag'] = bag

    # print(request.session['bag'])  prints to the console to test bag content

    return redirect(reverse('view_bag'))  # redirect user back to bag view


def remove_from_bag(request, item_id):  # it takes in the request and the id of the product the user wants to add
    """remove item from bag"""
    product = get_object_or_404(Product, pk=item_id)

    print(item_id)
    try:
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        bag = request.session.get('bag', {})

        if size:
            """
            So if size is in request.post. We'll want to delete that size key in the items by size dictionary.
            Also if that's the only size they had in the bag.
            In other words, if the items by size dictionary is now empty which will evaluate to false.
            We might as well remove the entire item id so we don't end up with an empty items
            by size dictionary hanging around.
            """
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
                messages.success(request, f'Removed {size.upper()} {product.name} from bag')

        else:
            """If there's no size that logic is quite simple and we can remove the item
            entirely by using the pop function."""
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from bag')


        # And then overwrite the variable in the session with the updated version.
        request.session['bag'] = bag

        print(request.session['bag'])  # prints to the console to test bag content

        return HttpResponse(status=200)  # Because this view will be posted to from a JavaScript function. We want to return an actual 200 HTTP response.
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
    