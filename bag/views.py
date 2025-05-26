from django.shortcuts import render, redirect

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):  # it takes in the request and the id of the product the user wants to add
    """add a quantity of the product to the bag """

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
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}  # if item id is not already in bag, added like this in case of same item different sizes
    else:
        # And finally we'll add the item to the bag or update the quantity if it already exists.
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    # And then overwrite the variable in the session with the updated version.
    request.session['bag'] = bag

    # print(request.session['bag'])  prints to the console to test bag content

    return redirect(redirect_url)  # redirect user back to redirect url
