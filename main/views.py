from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import  Order, Tile, SanitaryItem
from twilio.rest import Client
from .forms import  TileForm, SanitaryItemForm, OrderForm, OrderTileDetailsFormSet,OrderSanitaryDetailsFormSet
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

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
GOOGLE_DRIVE_CREDENTIALS_FILE = 'credentials.json'

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def inventory_home(request):
    return render(request, 'inventory/home.html')

@login_required
def order_home(request):
    return render(request, 'orders/home.html')

# List and manage Tiles
@login_required
def list_tiles(request):
    tiles = Tile.objects.all()
    return render(request, 'inventory/list_tiles.html', {'tiles': tiles})

@login_required
def add_tile(request):
    if request.method == 'POST':
        form = TileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_tiles')  # Redirect to the tiles list after adding
    else:
        form = TileForm()
    return render(request, 'inventory/add_tile.html', {'form': form})

@login_required
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
@login_required
def list_sanitary_items(request):
    items = SanitaryItem.objects.all()
    return render(request, 'inventory/list_sanitary_items.html', {'items': items})

# Add a new sanitary item
@login_required
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
@login_required
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

@login_required
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
@login_required
def get_available_stock(request):
    article_number = request.GET.get('article_number')
    try:
        tile = Tile.objects.get(article_number=article_number)
        return JsonResponse({'available_quantity': tile.quantity})
    except Tile.DoesNotExist:
        return JsonResponse({'available_quantity': 0})

@login_required
def create_sanitaryorder(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset1 = OrderSanitaryDetailsFormSet(request.POST)
        
        if order_form.is_valid() and formset1.is_valid():
            # Save the Order instance
            order = order_form.save(commit=False)  # Don't save to the database yet

            # Get the tiles_total value from the POST data
            sanitary_total = request.POST.get('sanitary_total',0)
            order.sanitary_total = sanitary_total
            
            # Save the updated Order instance to the database
            order.save()

            # Save the formset (OrderTileDetailsFormSet) related to this order
            formset1.instance = order
            formset1.save()

            return redirect('create_sanitaryorder')  # Replace with your success page
    else:
        order_form = OrderForm()
        formset1 = OrderSanitaryDetailsFormSet()

    return render(request, 'orders/create_sanitaryorder.html', {
        'order_form': order_form,
        'formset1': formset1

    })
@login_required
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

@login_required
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

@login_required
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



def upload_to_google_drive(file_path):
    """
    Uploads a file to Google Drive and returns a public URL.
    """
    # Authenticate using the service account credentials
    creds = Credentials.from_service_account_file(GOOGLE_DRIVE_CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])
    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'mimeType': 'application/pdf'
    }
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    # Upload the file
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Make the file publicly accessible
    file_id = uploaded_file.get('id')
    drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()

    # Get the public URL
    public_url = f"https://drive.google.com/uc?id={file_id}"
    return public_url


def send_whatsapp_message_with_attachment(phone_number, media_url):
    """
    Send a WhatsApp message using Twilio's API with the uploaded file URL as an attachment.
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        # Send the WhatsApp message using the public Google Drive URL
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:+{phone_number}',
            media_url=[media_url],
            body="Order details sent as a PDF attachment."
        )
        print(f"Sent WhatsApp message with SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


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


def tileorder_detail(request, order_id):
    """
    Handles order detail view and sends the WhatsApp message.
    """
    order = get_object_or_404(Order, pk=order_id)
    tile_details = order.tile_details.all()

    # Calculate the total amount
    total_amount = sum(tile.price for tile in tile_details)

    if request.method == "POST" and 'send_whatsapp' in request.POST:
        # Generate PDF locally
        pdf_path = generate_pdf_from_url(request, order_id)

        # Upload the PDF to Google Drive and get the public URL
        media_url = upload_to_google_drive(pdf_path)

        # Send WhatsApp message with the public URL
        success = send_whatsapp_message_with_attachment(order.customer_phone, media_url)

        if success:
            return render(request, 'orders/tileorder_detail.html', {
                'order': order,
                'tile_details': tile_details,
                'total_amount': total_amount,
                'message_sent': True,
            })
        else:
            return render(request, 'orders/tileorder_detail.html', {
                'order': order,
                'tile_details': tile_details,
                'total_amount': total_amount,
                'message_sent': False,
            })

    return render(request, 'orders/tileorder_detail.html', {
        'order': order,
        'tile_details': tile_details,
        'total_amount': total_amount,
    })
