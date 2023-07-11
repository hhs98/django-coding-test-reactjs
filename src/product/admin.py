from django.contrib import admin
from product.models import (
    Variant,
    Product,
    ProductVariant,
    ProductVariantPrice,
    ProductImage,
)

# Register your models here.
admin.site.register(Variant)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantPrice)
admin.site.register(ProductImage)
