"""Models for the shop_admin app."""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .fields import DefaultImageField


class Category(models.Model):
    """Category model for organizing products."""

    name = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        """Meta options for Category model."""
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """Override save method to automatically generate slug."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(models.Model):
    """User model representing customers in the shop."""

    LANGUAGE_CHOICES = [
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
    ]

    user_id = models.IntegerField(unique=True)
    user_username = models.CharField(max_length=255, null=True, blank=True)
    user_fullname = models.CharField(max_length=255)
    user_phone = models.CharField(max_length=20)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')

    def __str__(self):
        return self.user_fullname


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model representing items available for purchase."""

    product_name = models.CharField(max_length=255)
    product_name_ru = models.CharField(max_length=255)
    photo = DefaultImageField(upload_to='products/', blank=True, null=True)
    photo_2 = DefaultImageField(upload_to='products/', blank=True, null=True)
    photo_3 = DefaultImageField(upload_to='products/', blank=True, null=True)
    price = models.IntegerField()
    description = models.TextField()
    description_ru = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True
    )
    sizes = models.ManyToManyField(
        Size,
        related_name='products',
        blank=True
    )

    colors = models.ManyToManyField(
        Color,
        related_name='products',
        blank=True
    )
    def __str__(self):
        return self.product_name

    @property
    def all_images(self):
        """Return all images for this product."""
        images = []
        if self.photo:
            images.append(self.photo)
        if self.photo_2:
            images.append(self.photo_2)
        if self.photo_3:
            images.append(self.photo_3)
        return images


class ConnectUs(models.Model):
    """Model for storing contact information text."""

    text = models.TextField()

    def __str__(self):
        return self.text[:50]


class SocialMedia(models.Model):
    """Model for storing social media links."""

    name = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed"

class Order(models.Model):
    """Order model representing customer purchases."""

    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('accept', 'Accepted'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting'  # ✅ 'pending' o‘rniga 'waiting'
    )
    phone = models.CharField(max_length=20)
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.user.user_fullname}"


class Basket(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='basket_items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='basket_items'
    )

    number = models.IntegerField()  # Quantity

    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='basket_items'
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='basket_items'
    )

    class Meta:
        unique_together = ('user', 'product', 'color', 'size')

    def __str__(self):
        try:
            user_name = self.user.user_fullname if self.user else "Unknown user"
            product_name = self.product.product_name if self.product else "Unknown product"
            color_name = self.color.color_name if self.color else ""
            size_name = self.size.size_name if self.size else ""

            return f"{user_name} - {product_name} ({self.number})" + \
                (f" - {color_name}" if color_name else "") + \
                (f" - {size_name}" if size_name else "")
        except Exception as e:
            return f"Basket (xato): {e}"



class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ kerak bo‘lsa


