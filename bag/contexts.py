from decimal import Decimal  # more accurate than float better with money
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

# quantity changed to item_ data because Since there are now two different types of data that might be in our bag items.
# In the case of an item with no sizes. The item data will just be the quantity.
# But in the case of an item that has sizes the sitem data will be a dictionary of all the items by size.

def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0

    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():  # The items() method returns a view object that displays a list of dictionary's (key, value) tuple pairs.
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price
            product_count += item_data
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,  # src code says item_data but this is not right!!!
                    'product': product,
                    'size': size,
                })
    



    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE/100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,

    }

    return context