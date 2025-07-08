"""Admin configuration for the shop_admin app."""
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings

from unfold.admin import ModelAdmin, TabularInline

from .models import (
    User,
    Product,
    ConnectUs,
    SocialMedia,
    Order,
    OrderDetail,
    Basket,
    Category,
    Size,
    Color,
)


@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin configuration for Category model."""

    list_display = ('name', 'name_ru', 'slug', 'product_count')
    search_fields = ('name', 'name_ru', 'description')
    prepopulated_fields = {'slug': ('name', 'name_ru')}

    def product_count(self, obj):
        """Display the number of products in this category."""
        return obj.products.count()

    product_count.short_description = 'Products'


@admin.register(User)
class UserAdmin(ModelAdmin):
    """Admin configuration for User model."""

    list_display = ('user_fullname', 'user_username', 'user_id', 'user_phone')
    search_fields = ('user_fullname', 'user_username', 'user_id')
    list_filter = ('user_username',)





@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """Admin configuration for Product model."""

    list_display = (
        'product_name',
        'category',
        'price',
        'display_photo',
        'short_description',
        'display_sizes',
        'display_colors',  # yangi qator
        'image_count'
    )
    search_fields = ('product_name', 'description')
    list_filter = ('category', 'sizes', 'colors', 'price')
    autocomplete_fields = ['category']
    # Use a horizontal filter interface for sizes
    filter_horizontal = ('sizes', 'colors')

    # Standard Django actions
    actions = ['duplicate_product']

    fieldsets = (
        (None, {
            'fields': ('product_name', 'product_name_ru', 'category', 'price')
        }),
        ('Images', {
            'fields': ('photo', 'photo_2', 'photo_3'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('description','description_ru'),
            'classes': ('collapse',)
        }),
        ('Sizes', {
            'fields': ('sizes',),
            'description': 'Select available sizes for this product'
        }),
        ('Colors', {
        'fields': ('colors',),
        'description': 'Select available colors for this product'
        }),
    )

    def image_count(self, obj):
        """Display the number of additional images."""
        count = 0
        if hasattr(obj, 'photo_2') and obj.photo_2:
            count += 1
        if hasattr(obj, 'photo_3') and obj.photo_3:
            count += 1
        if count == 0:
            return "—"
        return f"{count} additional image{'s' if count > 1 else ''}"

    image_count.short_description = 'Additional Images'


    def duplicate_product(self, request, queryset):
        """Duplicate selected products, shu jumladan sizes va colors bilan."""
        for product in queryset:
            new_product = Product.objects.create(
                product_name=f"Copy of {product.product_name}",
                product_name_ru=f"Copy of {product.product_name_ru}",
                photo=product.photo,
                price=product.price,
                description=product.description,
                description_ru=product.description_ru,
                category=product.category
            )
            # Sizes ni nusxalash
            new_product.sizes.set(product.sizes.all())

            # Colors ni nusxalash (yangilandi)
            new_product.colors.set(product.colors.all())

            # Qo‘shimcha fotosuratlar
            if hasattr(product, 'photo_2') and product.photo_2:
                new_product.photo_2 = product.photo_2
            if hasattr(product, 'photo_3') and product.photo_3:
                new_product.photo_3 = product.photo_3

            new_product.save()

        self.message_user(
            request,
            f"{queryset.count()} product(s) duplicated successfully."
        )

    duplicate_product.short_description = "Duplicate selected products"

    def display_sizes(self, obj):
        """Display the sizes available for this product."""
        sizes = obj.sizes.all()
        if not sizes:
            return "—"
        if len(sizes) <= 3:
            return ", ".join([size.name for size in sizes])
        return f"{sizes.count()} sizes"

    display_sizes.short_description = 'Sizes'

    def display_colors(self, obj):
        colors = obj.colors.all()
        if not colors:
            return "—"
        if len(colors) <= 3:
            return ", ".join([color.name for color in colors])
        return f"{colors.count()} colors"

    display_colors.short_description = 'Colors'

    def display_photo(self, obj):
        """Display product photo as an image."""
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="object-fit: cover; border-radius: 4px;" />',
                obj.photo.url
            )
        # Use default image if no photo is available
        return format_html(
            '<img src="{}" width="40" height="40" '
            'style="object-fit: cover; border-radius: 4px;" />',
            settings.DEFAULT_PRODUCT_IMAGE
        )

    display_photo.short_description = 'Photo'

    def short_description(self, obj):
        """Display a shortened version of the description."""
        if not obj.description:
            return "—"
        if len(obj.description) > 40:
            return obj.description[:40] + '…'
        return obj.description

    short_description.short_description = 'Description'


@admin.register(ConnectUs)
class ConnectUsAdmin(ModelAdmin):
    """Admin configuration for ConnectUs model."""

    list_display = ('id', 'short_text')

    def short_text(self, obj):
        """Display a shortened version of the text."""
        if not obj.text:
            return "—"
        if len(obj.text) > 80:
            return obj.text[:80] + '…'
        return obj.text

    short_text.short_description = 'Text'


@admin.register(SocialMedia)
class SocialMediaAdmin(ModelAdmin):
    """Admin configuration for SocialMedia model."""

    list_display = ('name', 'url')
    search_fields = ('name', 'url')


class OrderDetailInline(TabularInline):
    """Inline admin for OrderDetail model."""

    model = OrderDetail
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """Admin configuration for Order model."""

    list_display = ('id', 'user', 'status', 'phone', 'created_time')
    list_filter = ('status', 'created_time')
    search_fields = ('user__user_fullname', 'phone')
    inlines = [OrderDetailInline]

    # Standard Django actions
    actions = ['mark_as_completed', 'mark_as_processing']

    def mark_as_completed(self, request, queryset):
        """Mark selected orders as completed."""
        queryset.update(status='completed')
        self.message_user(
            request,
            f"{queryset.count()} order(s) marked as completed."
        )

    mark_as_completed.short_description = "Mark as completed"

    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing."""
        queryset.update(status='processing')
        self.message_user(
            request,
            f"{queryset.count()} order(s) marked as processing."
        )

    mark_as_processing.short_description = "Mark as processing"


@admin.register(Basket)
class BasketAdmin(ModelAdmin):
    list_display = ('user', 'product', 'number', 'color', 'size')
    list_filter = ('user', 'product', 'color', 'size')
    search_fields = ('user__user_fullname', 'product__product_name')


