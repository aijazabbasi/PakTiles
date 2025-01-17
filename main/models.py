from django.db import models
from django.conf import settings


class Tile(models.Model):
    tile_id = models.AutoField(primary_key=True, editable=False)
    category = models.CharField(max_length=255, default=None)
    article_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255, default=None)
    tile_size = models.CharField(max_length=100)
    box_size = models.CharField(max_length=255, default=None)
    peiece_per_box = models.CharField(max_length=255, default=None)
    sale_unit = models.CharField(max_length=255, default=None)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.article_number


class SanitaryItem(models.Model):
    item_id = models.AutoField(primary_key=True, editable=False)
    article_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15)
    bill_number = models.IntegerField(null=True)
    order_date = models.DateField(auto_now_add=True)
    tiles_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sanitary_total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    # sales_person = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="orders",
    #     editable=False
    # )
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"

class OrderTileDetails(models.Model):
    tiledetail_id = models.AutoField(primary_key=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tile_details')
    category = models.CharField(max_length=255)
    article_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    tile_size = models.CharField(max_length=100)
    box_size = models.CharField(max_length=255)
    peiece_per_box = models.CharField(max_length=255)
    sale_unit = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # rate * quantity

    def save(self, *args, **kwargs):
        self.price = self.rate * self.quantity  # Automatically calculate price
        super(OrderTileDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.article_number} - {self.quantity}"


class OrderSanitaryDetails(models.Model):
    sanitary_itemid = models.AutoField(primary_key=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sanitary_details')
    article_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # rate * quantity

    def save(self, *args, **kwargs):
        self.price = self.rate * self.quantity  # Automatically calculate price
        super(OrderSanitaryDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.article_number} - {self.quantity}"

class RefundOrder(models.Model):
    refund_order_id = models.AutoField(primary_key=True, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15)
    bill_number = models.IntegerField(null=True)
    order_date = models.DateField(auto_now_add=True)
    tiles_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sanitary_total = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    # sales_person = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="orders",
    #     editable=False
    # )
    def __str__(self):
        return f"Refund Order {self.refund_order_id} - {self.customer_name}"

class RefundOrderTileDetails(models.Model):
    tiledetail_id = models.AutoField(primary_key=True, editable=False)
    Refundorder = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, related_name='tilerefund_details')
    category = models.CharField(max_length=255)
    article_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    tile_size = models.CharField(max_length=100)
    box_size = models.CharField(max_length=255)
    peiece_per_box = models.CharField(max_length=255)
    sale_unit = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # rate * quantity

    def save(self, *args, **kwargs):
        self.price = self.rate * self.quantity  # Automatically calculate price
        super(RefundOrderTileDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.article_number} - {self.quantity}"


class RefundOrderSanitaryDetails(models.Model):
    sanitary_itemid = models.AutoField(primary_key=True, editable=False)
    Refundorder = models.ForeignKey(RefundOrder, on_delete=models.CASCADE, related_name='sanitaryrefund_details')
    article_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # rate * quantity

    def save(self, *args, **kwargs):
        self.price = self.rate * self.quantity  # Automatically calculate price
        super(RefundOrderSanitaryDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.article_number} - {self.quantity}"
