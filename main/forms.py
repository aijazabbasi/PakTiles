from django import forms
from django.forms import inlineformset_factory
from .models import Tile, SanitaryItem, Order, OrderTileDetails, OrderSanitaryDetails, RefundOrder, RefundOrderSanitaryDetails,RefundOrderTileDetails

class TileForm(forms.ModelForm):
    class Meta:
        model = Tile
        fields = ['category', 'article_number', 'description', 'tile_size', 'box_size', 'peiece_per_box', 'sale_unit', 'rate', 'quantity']

class SanitaryItemForm(forms.ModelForm):
    class Meta:
        model = SanitaryItem
        fields = ['article_number', 'name', 'brand', 'rate', 'quantity']

# Order Form
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'bill_number']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),          
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['customer_phone'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['bill_number'].widget.attrs.update({'class': 'form-control form-control-sm'})

# OrderTileDetails Form
class OrderTileDetailsForm(forms.ModelForm):
    class Meta:
        model = OrderTileDetails
        fields = ['category', 'article_number', 'description', 'tile_size', 'box_size',
                  'peiece_per_box', 'sale_unit', 'rate', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['article_number'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['description'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['tile_size'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['box_size'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['peiece_per_box'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['sale_unit'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['rate'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control form-control-sm'})
        
# Inline Formset for OrderTileDetails
OrderTileDetailsFormSet = inlineformset_factory(
    Order, OrderTileDetails, form=OrderTileDetailsForm, extra=1, can_delete=True
)

# OrderSaitaryDetails Form
class OrderSanitaryDetailsForm(forms.ModelForm):
    class Meta:
        model = OrderSanitaryDetails
        fields = ['article_number', 'name', 'brand', 'rate', 'quantity']

OrderSanitaryDetailsFormSet = inlineformset_factory(
    Order, OrderSanitaryDetails, form=OrderSanitaryDetailsForm, extra=1, can_delete=True
)


class RefundOrderForm(forms.ModelForm):
    class Meta:
        model = RefundOrder
        fields = ['customer_name', 'customer_phone','bill_number']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),          
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['customer_phone'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['bill_number'].widget.attrs.update({'class': 'form-control form-control-sm'})

# OrderTileDetails Form
class RefundOrderTileDetailsForm(forms.ModelForm):
    class Meta:
        model = RefundOrderTileDetails
        fields = ['category', 'article_number', 'description', 'tile_size', 'box_size',
                  'peiece_per_box', 'sale_unit', 'rate', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['article_number'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['description'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['tile_size'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['box_size'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['peiece_per_box'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['sale_unit'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['rate'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control form-control-sm'})
        
# Inline Formset for OrderTileDetails
RefundOrderTileDetailsFormSet = inlineformset_factory(
    RefundOrder, RefundOrderTileDetails, form=RefundOrderTileDetailsForm, extra=1, can_delete=True
)

# OrderSaitaryDetails Form
class RefundOrderSanitaryDetailsForm(forms.ModelForm):
    class Meta:
        model = RefundOrderSanitaryDetails
        fields = ['article_number', 'name', 'brand', 'rate', 'quantity']

RefundOrderSanitaryDetailsFormSet = inlineformset_factory(
    RefundOrder, RefundOrderSanitaryDetails, form=RefundOrderSanitaryDetailsForm, extra=1, can_delete=True
)