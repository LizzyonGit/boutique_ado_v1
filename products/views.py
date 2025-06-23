from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages 
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm
from django.contrib.auth.decorators import login_required

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

@login_required
def add_product(request):
    """Add a product to the store"""
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorised to do this')
        return redirect(reverse('home'))
    if request.method == 'POST':  # post handler
        form = ProductForm(request.POST, request.FILES)  # new instance of product form from request.Post and request.files (images)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product')
            return redirect(reverse('product_detail', args=[product.id]))  # redirect to added product 
        else:
            messages.error(request, 'Failed to add product, ensure the form is valid')
    else:
        form = ProductForm()  # empty form
    
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

@login_required
def edit_product(request, product_id):
    """edit product"""
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorised to do this')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully edited product')
            return redirect(reverse('product_detail', args=[product.id]))  # redirect to product detail page using the product id
        else:
            messages.error(request, 'Failed to update product. Correct the invalid fields')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product
    }

    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """delete product"""
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorised to do this')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted')  # product.name raises error

    return redirect(reverse('products'))


