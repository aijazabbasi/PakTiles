from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import FileResponse
from .models import  Order, Tile, SanitaryItem, RefundOrder
from twilio.rest import Client
from .forms import  TileForm, SanitaryItemForm, OrderForm, OrderTileDetailsFormSet,OrderSanitaryDetailsFormSet, RefundOrderForm, RefundOrderTileDetailsFormSet, RefundOrderSanitaryDetailsFormSet
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import pdfkit
import os
from django.template.loader import render_to_string
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from django.urls import reverse
from django.db.models import Q

TWILIO_ACCOUNT_SID = 'AC6cd81f119397fce8951f4b259203b845' #os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = 'd64ea652702c2f08c63c44e1ac29c8b4' #os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
GOOGLE_DRIVE_CREDENTIALS_FILE = 'credentials.json'


def home(request):
    return render(request, 'home.html')


def inventory_home(request):
    return render(request, 'inventory/home.html')


def order_home(request):
    return render(request, 'orders/home.html')

# List and manage Tiles

def list_tiles(request):
    query = request.GET.get('query','')
    tiles = Tile.objects.all()
    if query:
        tiles = tiles.filter(
            Q(category__icontains=query) | Q(article_number__icontains=query)
        )
    
    return render(request, 'inventory/list_tiles.html', {'tiles': tiles})


def add_tile(request):
    if request.method == 'POST':
        form = TileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_tiles')  # Redirect to the tiles list after adding
    else:
        form = TileForm()
    return render(request, 'inventory/add_tile.html', {'form': form})


def edit_tile(request, tile_id):
    tile = get_object_or_404(Tile, tile_id=tile_id)
    if request.method == 'POST':
        form = TileForm(request.POST, instance=tile)
        if form.is_valid():
            form.save()
            return redirect('list_tiles')  # Redirect to the tiles list after editing
    else:
        form = TileForm(instance=tile)
    return render(request, 'inventory/edit_tile.html', {'form': form, 'tile': tile})

# Add similar views for Sanitary Items when their model is ready

# List all sanitary items

def list_sanitary_items(request):
    query = request.GET.get('query','')
    items = SanitaryItem.objects.all()

    if query:
        items = items.filter(
            Q(article_number__icontains=query) | Q(name__icontains=query) | Q(brand__icontains=query)
        )
    return render(request, 'inventory/list_sanitary_items.html', {'items': items, 'query':query})

# Add a new sanitary item

def add_sanitary_item(request):
    if request.method == 'POST':
        form = SanitaryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_sanitary_items')
    else:
        form = SanitaryItemForm()
    return render(request, 'inventory/add_sanitary_item.html', {'form': form})

# Edit an existing sanitary item

def edit_sanitary_item(request, item_id):
    item = get_object_or_404(SanitaryItem, pk=item_id)
    if request.method == 'POST':
        form = SanitaryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('list_sanitary_items')
    else:
        form = SanitaryItemForm(instance=item)
    return render(request, 'inventory/edit_sanitary_item.html', {'form': form, 'item': item})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderTileDetailsFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            # Save the Order instance (but don't commit yet)
            order = order_form.save(commit=False)
            order.sales_person = request.user

            # Get the tiles_total value from the POST data
            tiles_total = request.POST.get('tiles_total', 0)
            order.tiles_total = tiles_total

            # Validate quantities against available stock in Tile model
            tile_details = formset.cleaned_data
            for form in formset:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    try:
                        tile = Tile.objects.get(article_number=article_number)
                    except Tile.DoesNotExist:
                        form.add_error('article_number', f"Tile with article number {article_number} does not exist.")
                        continue

                    # Check if the quantity ordered exceeds available stock
                    if quantity_ordered > tile.quantity:
                        form.add_error('quantity', f"Insufficient stock for tile {tile.article_number}. Only {tile.quantity} available.")
                        continue

            # If there are no errors, save the order and update tile stock
            if not any(form.errors for form in formset):
                # Save the Order instance to the database
                order.save()

                # Save the formset (OrderTileDetailsFormSet) related to this order
                formset.instance = order
                formset.save()

                # Deduct the ordered quantity from the stock in Tile model
                for form in formset:
                    article_number = form.cleaned_data.get('article_number')
                    quantity_ordered = form.cleaned_data.get('quantity')

                    if article_number and quantity_ordered:
                        tile = Tile.objects.get(article_number=article_number)
                        tile.quantity -= quantity_ordered
                        tile.save()

                return redirect('tileorder_list')  # Redirect to the order creation page (or to another page)

    else:
        order_form = OrderForm()
        formset = OrderTileDetailsFormSet()

    return render(request, 'orders/create_order.html', {
        'order_form': order_form,
        'formset': formset
    })

def get_available_stock(request):
    article_number = request.GET.get('article_number')
    try:
        tile = Tile.objects.get(article_number=article_number)
        return JsonResponse({'available_quantity': tile.quantity})
    except Tile.DoesNotExist:
        return JsonResponse({'available_quantity': 0})


def create_sanitaryorder(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset1 = OrderSanitaryDetailsFormSet(request.POST)
        
        if order_form.is_valid() and formset1.is_valid():
            # Save the Order instance
            order = order_form.save(commit=False)  # Don't save to the database yet
            order.sales_person = request.user

            # Get the tiles_total value from the POST data
            sanitary_total = request.POST.get('sanitary_total',0)
            order.sanitary_total = sanitary_total

            # Validate quantities against available stock in Tile model
            sanitary_details = formset1.cleaned_data
            for form in formset1:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    try:
                        sanitaryitem = SanitaryItem.objects.get(article_number=article_number)
                    except SanitaryItem.DoesNotExist:
                        form.add_error('article_number', f"SanitaryItem with article number {article_number} does not exist.")
                        continue

                    # Check if the quantity ordered exceeds available stock
                    if quantity_ordered > sanitaryitem.quantity:
                        form.add_error('quantity', f"Insufficient stock for tile {sanitaryitem.article_number}. Only {sanitaryitem.quantity} available.")
                        continue

            # If there are no errors, save the order and update tile stock
            if not any(form.errors for form in formset1):
                # Save the Order instance to the database
                order.save()

            # Save the formset (OrderTileDetailsFormSet) related to this order
            formset1.instance = order
            formset1.save()

            # Deduct the ordered quantity from the stock in Tile model
            for form in formset1:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    sanitaryitem = SanitaryItem.objects.get(article_number=article_number)
                    sanitaryitem.quantity -= quantity_ordered
                    sanitaryitem.save()

            return redirect('sanitaryorder_list')  # Replace with your success page
    else:
        order_form = OrderForm()
        formset1 = OrderSanitaryDetailsFormSet()

    return render(request, 'orders/create_sanitaryorder.html', {
        'order_form': order_form,
        'formset1': formset1

    })
    

def get_tile_data(request):
    article_number = request.GET.get('article_number')
    tile = Tile.objects.filter(article_number=article_number).first()
    if tile:
        data = {
            'category': tile.category,
            'description': tile.description,
            'tile_size': tile.tile_size,
            'box_size': tile.box_size,
            'peiece_per_box': tile.peiece_per_box,
            'sale_unit': tile.sale_unit,
            'rate': tile.rate,
        }
    else:
        data = {}
    return JsonResponse(data)


def get_sanitary_data(request):
    article_number = request.GET.get('article_number')
    sanitaryitem = SanitaryItem.objects.filter(article_number=article_number).first()
    if sanitaryitem:
        data = {
            'name': sanitaryitem.name,
            'brand': sanitaryitem.brand,
            'rate': sanitaryitem.rate,
        }
    else:
        data = {}
    return JsonResponse(data)


def tileorder_list(request):
    """
    View to list only orders that have at least one tile detail associated with them.
    Orders can be searched by customer name or phone and are sorted by order_id in descending order.
    """
    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Filter orders with related tile details and apply search
    orders = Order.objects.filter(tile_details__isnull=False).distinct()

    if search_query:
        orders = orders.filter(
            Q(customer_name__icontains=search_query) | Q(customer_phone__icontains=search_query)
        )

    # Sort the results by order_id in descending order
    orders = orders.order_by('-order_id')

    return render(request, 'orders/tileorder_list.html', {'orders': orders, 'search_query': search_query})


def sanitaryorder_list(request):
    """
    View to list only orders that have at least one tile detail associated with them.
    Orders can be searched by customer name or phone and are sorted by order_id in descending order.
    """
    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Filter orders with related tile details and apply search
    orders = Order.objects.filter(sanitary_details__isnull=False).distinct()

    if search_query:
        orders = orders.filter(
            Q(customer_name__icontains=search_query) | Q(customer_phone__icontains=search_query)
        )

    # Sort the results by order_id in descending order
    orders = orders.order_by('-order_id')

    return render(request, 'orders/sanitaryorder_list.html', {'orders': orders, 'search_query': search_query})

def generate_pdf_from_url(request, order_id):
    """
    Generates a PDF from a URL (same HTML template format) and saves it locally.
    """
    # Build the full URL for the order detail page with hide_button parameter
    url = f"{request.build_absolute_uri(reverse('tileorder_detail', args=[order_id]))}?hide_button=true"

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': ''  # Suppress wkhtmltopdf's output
    }

    # Define where to save the file
    save_dir = os.path.join('media', 'order_pdfs')
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
    pdf_path = os.path.join(save_dir, f"order_{order_id}.pdf")

    # Generate the PDF from the URL
    pdfkit.from_url(url, pdf_path, options=options, configuration=config)

    return pdf_path

def generate_pdf_from_url_sanitaryitem(request, order_id):
    """
    Generates a PDF from a URL (same HTML template format) and saves it locally.
    """
    # Build the full URL for the order detail page with hide_button parameter
    url = f"{request.build_absolute_uri(reverse('sanitaryorder_detail', args=[order_id]))}?hide_button=true"

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': ''  # Suppress wkhtmltopdf's output
    }

    # Define where to save the file
    save_dir = os.path.join('media', 'order_pdfs')
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
    pdf_path = os.path.join(save_dir, f"sanitaryorder_{order_id}.pdf")

    # Generate the PDF from the URL
    pdfkit.from_url(url, pdf_path, options=options, configuration=config)

    return pdf_path


# Assuming you have a function generate_pdf_from_url(request, order_id) that generates the PDF locally.
def tileorder_detail(request, order_id):
    """
    Handles order detail view and provides a print preview.
    """
    order = get_object_or_404(Order, pk=order_id)
    tile_details = order.tile_details.all()

    # Calculate the total amount
    total_amount = sum(tile.price for tile in tile_details)

    # Initialize paid amount and balance
    # paid_amount = 0
    # balance_amount = total_amount

    if request.method == "POST":
        # if 'paid_amount' in request.POST:
        #     try:
        #         paid_amount = float(request.POST.get('paid_amount', 0))
        #     except ValueError:
        #         paid_amount = 0

        #     balance_amount = float(total_amount) - float(paid_amount)

        if 'print_pdf' in request.POST:
            # Generate PDF locally
            pdf_path = generate_pdf_from_url(request, order_id)

            # Serve the PDF as a response
            pdf_file = open(pdf_path, 'rb')
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="order_{order_id}.pdf"'

            return response

    return render(request, 'orders/tileorder_detail.html', {
        'order': order,
        'tile_details': tile_details,
        'total_amount': total_amount,
        # 'paid_amount': paid_amount,
        # 'balance_amount': balance_amount,
        'show_print_button': True,
    })



def sanitaryorder_detail(request, order_id):
    """
    Handles order detail view and provides a print preview.
    """
    order = get_object_or_404(Order, pk=order_id)
    sanitary_details = order.sanitary_details.all()

    # Calculate the total amount
    total_amount = sum(sanitaryitem.price for sanitaryitem in sanitary_details)

    if request.method == "POST" and 'print_pdf' in request.POST:
        # Generate PDF locally
        pdf_path = generate_pdf_from_url_sanitaryitem(request, order_id)

        # Serve the PDF as a response
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="sanitaryorder_{order_id}.pdf"'

        return response

    return render(request, 'orders/sanitaryorder_detail.html', {
        'order': order,
        'sanitary_details': sanitary_details,
        'total_amount': total_amount,
        'show_print_button': True,
    })


def create_refundorder(request):
    if request.method == 'POST':
        order_form = RefundOrderForm(request.POST)
        formset = RefundOrderTileDetailsFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            # Save the Order instance (but don't commit yet)
            order = order_form.save(commit=False)
            order.sales_person = request.user

            # Get the tiles_total value from the POST data
            tiles_total = request.POST.get('tiles_total', 0)
            order.tiles_total = tiles_total

            # Validate quantities against available stock in Tile model
            tile_details = formset.cleaned_data
            for form in formset:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    try:
                        tile = Tile.objects.get(article_number=article_number)
                    except Tile.DoesNotExist:
                        form.add_error('article_number', f"Tile with article number {article_number} does not exist.")
                        continue

            # If there are no errors, save the order and update tile stock
            if not any(form.errors for form in formset):
                # Save the Order instance to the database
                order.save()

                # Save the formset (OrderTileDetailsFormSet) related to this order
                formset.instance = order
                formset.save()

                # Deduct the ordered quantity from the stock in Tile model
                for form in formset:
                    article_number = form.cleaned_data.get('article_number')
                    quantity_ordered = form.cleaned_data.get('quantity')

                    if article_number and quantity_ordered:
                        tile = Tile.objects.get(article_number=article_number)
                        tile.quantity += quantity_ordered
                        tile.save()

                return redirect('tilerefundorder_list')  # Redirect to the order creation page (or to another page)

    else:
        order_form = RefundOrderForm()
        formset = RefundOrderTileDetailsFormSet()

    return render(request, 'orders/create_refundorder.html', {
        'order_form': order_form,
        'formset': formset
    })

def create_sanitaryrefundorder(request):
    if request.method == 'POST':
        order_form = RefundOrderForm(request.POST)
        formset1 = RefundOrderSanitaryDetailsFormSet(request.POST)
        
        if order_form.is_valid() and formset1.is_valid():
            # Save the Order instance
            order = order_form.save(commit=False)  # Don't save to the database yet
            order.sales_person = request.user

            # Get the tiles_total value from the POST data
            sanitary_total = request.POST.get('sanitary_total',0)
            order.sanitary_total = sanitary_total

            # Validate quantities against available stock in Tile model
            sanitary_details = formset1.cleaned_data
            for form in formset1:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    try:
                        sanitaryitem = SanitaryItem.objects.get(article_number=article_number)
                    except SanitaryItem.DoesNotExist:
                        form.add_error('article_number', f"SanitaryItem with article number {article_number} does not exist.")
                        continue

            # If there are no errors, save the order and update tile stock
            if not any(form.errors for form in formset1):
                # Save the Order instance to the database
                order.save()

            # Save the formset (OrderTileDetailsFormSet) related to this order
            formset1.instance = order
            formset1.save()

            # Deduct the ordered quantity from the stock in Tile model
            for form in formset1:
                article_number = form.cleaned_data.get('article_number')
                quantity_ordered = form.cleaned_data.get('quantity')

                if article_number and quantity_ordered:
                    sanitaryitem = SanitaryItem.objects.get(article_number=article_number)
                    sanitaryitem.quantity += quantity_ordered
                    sanitaryitem.save()

            return redirect('sanitaryrefundorder_list')  # Replace with your success page
    else:
        order_form = RefundOrderForm()
        formset1 = RefundOrderSanitaryDetailsFormSet()

    return render(request, 'orders/create_sanitaryrefundorder.html', {
        'order_form': order_form,
        'formset1': formset1

    })

def tilerefundorder_list(request):
    """
    View to list only orders that have at least one tile detail associated with them.
    Orders can be searched by customer name or phone and are sorted by order_id in descending order.
    """
    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Filter orders with related tile details and apply search
    orders = RefundOrder.objects.filter(tilerefund_details__isnull=False).distinct()

    if search_query:
        orders = orders.filter(
            Q(customer_name__icontains=search_query) | Q(customer_phone__icontains=search_query)
        )

    # Sort the results by order_id in descending order
    orders = orders.order_by('-refund_order_id')

    return render(request, 'orders/tilerefundorder_list.html', {'orders': orders, 'search_query': search_query})

def tilerefundorder_detail(request, refund_order_id):
    """
    Handles order detail view and provides a print preview.
    """
    order = get_object_or_404(RefundOrder, pk=refund_order_id)
    tilerefund_details = order.tilerefund_details.all()

    # Calculate the total amount
    total_amount = sum(tile.price for tile in tilerefund_details)

    # Initialize paid amount and balance
    # paid_amount = 0
    # balance_amount = total_amount

    if request.method == "POST":
        # if 'paid_amount' in request.POST:
        #     try:
        #         paid_amount = float(request.POST.get('paid_amount', 0))
        #     except ValueError:
        #         paid_amount = 0

        #     balance_amount = float(total_amount) - float(paid_amount)

        if 'print_pdf' in request.POST:
            # Generate PDF locally
            pdf_path = generate_pdf_from_url_refund(request, refund_order_id)

            # Serve the PDF as a response
            pdf_file = open(pdf_path, 'rb')
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="refundorder_{refund_order_id}.pdf"'

            return response

    return render(request, 'orders/tilerefundorder_detail.html', {
        'order': order,
        'tilerefund_details': tilerefund_details,
        'total_amount': total_amount,
        # 'paid_amount': paid_amount,
        # 'balance_amount': balance_amount,
        'show_print_button': True,
    })


def generate_pdf_from_url_refund(request, refund_order_id):
    """
    Generates a PDF from a URL (same HTML template format) and saves it locally.
    """
    # Build the full URL for the order detail page with hide_button parameter
    url = f"{request.build_absolute_uri(reverse('tilerefundorder_detail', args=[refund_order_id]))}?hide_button=true"

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': ''  # Suppress wkhtmltopdf's output
    }

    # Define where to save the file
    save_dir = os.path.join('media', 'order_pdfs')
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
    pdf_path = os.path.join(save_dir, f"refundorder_{refund_order_id}.pdf")

    # Generate the PDF from the URL
    pdfkit.from_url(url, pdf_path, options=options, configuration=config)

    return pdf_path

def sanitaryrefundorder_list(request):
    """
    View to list only orders that have at least one tile detail associated with them.
    Orders can be searched by customer name or phone and are sorted by order_id in descending order.
    """
    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Filter orders with related tile details and apply search
    orders = RefundOrder.objects.filter(sanitaryrefund_details__isnull=False).distinct()

    if search_query:
        orders = orders.filter(
            Q(customer_name__icontains=search_query) | Q(customer_phone__icontains=search_query)
        )

    # Sort the results by order_id in descending order
    orders = orders.order_by('-refund_order_id')

    return render(request, 'orders/sanitaryrefundorder_list.html', {'orders': orders, 'search_query': search_query})


def sanitaryrefundorder_detail(request, refund_order_id):
    """
    Handles order detail view and provides a print preview.
    """
    order = get_object_or_404(RefundOrder, pk=refund_order_id)
    sanitaryrefund_details = order.sanitaryrefund_details.all()

    # Calculate the total amount
    total_amount = sum(sanitaryitem.price for sanitaryitem in sanitaryrefund_details)

    if request.method == "POST" and 'print_pdf' in request.POST:
        # Generate PDF locally
        pdf_path = generate_pdf_from_url_sanitaryitem_refund(request, refund_order_id)

        # Serve the PDF as a response
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="sanitaryrefundorder_{refund_order_id}.pdf"'

        return response

    return render(request, 'orders/sanitaryrefundorder_detail.html', {
        'order': order,
        'sanitaryrefund_details': sanitaryrefund_details,
        'total_amount': total_amount,
        'show_print_button': True,
    })

def generate_pdf_from_url_sanitaryitem_refund(request, refund_order_id):
    """
    Generates a PDF from a URL (same HTML template format) and saves it locally.
    """
    # Build the full URL for the order detail page with hide_button parameter
    url = f"{request.build_absolute_uri(reverse('sanitaryrefundorder_detail', args=[refund_order_id]))}?hide_button=true"

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': ''  # Suppress wkhtmltopdf's output
    }

    # Define where to save the file
    save_dir = os.path.join('media', 'order_pdfs')
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
    pdf_path = os.path.join(save_dir, f"sanitaryrefundorder_{refund_order_id}.pdf")

    # Generate the PDF from the URL
    pdfkit.from_url(url, pdf_path, options=options, configuration=config)

    return pdf_path

