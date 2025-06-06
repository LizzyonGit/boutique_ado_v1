from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages 
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category

# Create your views here.

def all_products(request):
    """A view to show all products,
    including sorting and search queries
    """
    products = Product.objects.all()
    #  below variables are equal to none at the top. Since we'll need to make sure those are defined in order to return the template properly when we're not using any sorting etc.
    query = None
    categories = None
    sort = None
    direction = None
    

    if request.GET:
        if 'sort' in request.GET:
                sortkey = request.GET['sort']
                sort = sortkey
                if sortkey == 'name':
                    sortkey = 'lower_name'  # in the event the user is sorting by name
                    products = products.annotate(lower_name=Lower('name'))
                if sortkey == 'category':
                    sortkey = 'category__name'  # sort on category name instead of id (I did not see the difference though)

                if 'direction' in request.GET:
                    direction = request.GET['direction']
                    if direction == 'desc':
                        sortkey = f'-{sortkey}'
                products = products.order_by(sortkey)  # actually sorting the products

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)  # so we can access the fields in the template

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, 'You did not enter any search criteria')
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    } 

    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """A view to show the product details
    """
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    } 

    return render(request, 'products/product_detail.html', context)
