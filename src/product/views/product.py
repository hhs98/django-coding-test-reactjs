import json
from typing import Any, Dict
from django.http import JsonResponse
from django.views import generic
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, OuterRef, Q
from django.forms.models import model_to_dict
from product.models import (
    Variant,
    Product,
    ProductVariant,
    ProductVariantPrice,
    ProductImage,
)


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        sku = request.POST.get('sku')
        description = request.POST.get('description')

        product_variants = json.loads(request.POST.get('product_variants'))
        product_variant_prices = json.loads(
            request.POST.get('product_variant_prices')
        )
        product_images = json.loads(request.POST.get('product_images'))

        product = Product.objects.create(
            title=title, sku=sku, description=description
        )

        for product_variant in product_variants:
            variant = Variant.objects.get(id=product_variant['option'])
            for tag in product_variant['tags']:
                ProductVariant.objects.create(
                    variant_title=tag,
                    variant=variant,
                    product=product,
                )

        for product_variant_price in product_variant_prices:
            product_variant_one = None
            product_variant_two = None
            product_variant_three = None

            variant_titles = product_variant_price['title'].split('/')
            print(variant_titles)
            if len(variant_titles) > 0 and variant_titles[0] != '':
                product_variant_one = ProductVariant.objects.get(
                    variant_title=variant_titles[0],
                    product=product,
                )
            if len(variant_titles) > 1 and variant_titles[1] != '':
                product_variant_two = ProductVariant.objects.get(
                    variant_title=variant_titles[1],
                    product=product,
                )
            if len(variant_titles) > 2 and variant_titles[2] != '':
                product_variant_three = ProductVariant.objects.get(
                    variant_title=variant_titles[2],
                    product=product,
                )

            ProductVariantPrice.objects.create(
                product_variant_one=product_variant_one,
                product_variant_two=product_variant_two,
                product_variant_three=product_variant_three,
                price=product_variant_price['price'],
                stock=product_variant_price['stock'],
                product=product,
            )

        for product_image in product_images:
            ProductImage.objects.create(
                product=product, file_path=product_image['path']
            )

        return JsonResponse({'status': 'success'})


class ProductEditView(generic.TemplateView):
    template_name = 'products/edit.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        product = Product.objects.get(id=kwargs['id'])
        # dict = {'title': 'xl/red/full', 'price': '100', 'stock': '10'}
        product_variant_prices = []
        for product_variant_price in product.productvariantprice_set.all():
            product_variant_prices.append(
                {
                    'title': product_variant_price.title(),
                    'price': product_variant_price.price,
                    'stock': product_variant_price.stock,
                }
            )

        # dict = {'option': 1, 'tags': ['xl', 'l', 'm']}
        product_variants = []
        for product_variant in product.productvariant_set.values_list(
            'variant__id', flat=True
        ).distinct():
            product_variants.append(
                {
                    'option': product_variant,
                    'tags': list(
                        product.productvariant_set.filter(
                            variant__id=product_variant
                        ).values_list('variant_title', flat=True)
                    ),
                }
            )

        context['object'] = model_to_dict(product)
        context['object']['product_variant_prices'] = product_variant_prices
        context['object']['product_variants'] = product_variants
        context['product'] = True
        print(context['object'])
        context['variants'] = list(variants.all())
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        title = request.POST.get('title')
        sku = request.POST.get('sku')
        description = request.POST.get('description')

        product_variants = json.loads(request.POST.get('product_variants'))
        product_variant_prices = json.loads(
            request.POST.get('product_variant_prices')
        )
        product_images = json.loads(request.POST.get('product_images'))

        product = Product.objects.get(id=kwargs['id'])
        product.title = title
        product.sku = sku
        product.description = description

        product.productvariant_set.all().delete()
        product.productvariantprice_set.all().delete()
        product.productimage_set.all().delete()

        for product_variant in product_variants:
            variant = Variant.objects.get(id=product_variant['option'])
            for tag in product_variant['tags']:
                ProductVariant.objects.create(
                    variant_title=tag,
                    variant=variant,
                    product=product,
                )

        for product_variant_price in product_variant_prices:
            product_variant_one = None
            product_variant_two = None
            product_variant_three = None

            variant_titles = product_variant_price['title'].split('/')
            print(variant_titles)
            if len(variant_titles) > 0 and variant_titles[0] != '':
                product_variant_one = ProductVariant.objects.get(
                    variant_title=variant_titles[0],
                    product=product,
                )
            if len(variant_titles) > 1 and variant_titles[1] != '':
                product_variant_two = ProductVariant.objects.get(
                    variant_title=variant_titles[1],
                    product=product,
                )
            if len(variant_titles) > 2 and variant_titles[2] != '':
                product_variant_three = ProductVariant.objects.get(
                    variant_title=variant_titles[2],
                    product=product,
                )

            ProductVariantPrice.objects.create(
                product_variant_one=product_variant_one,
                product_variant_two=product_variant_two,
                product_variant_three=product_variant_three,
                price=product_variant_price['price'],
                stock=product_variant_price['stock'],
                product=product,
            )

        for product_image in product_images:
            ProductImage.objects.create(
                product=product, file_path=product_image['path']
            )

        product.save()

        return JsonResponse({'status': 'success'})


class ProductListView(generic.TemplateView):
    template_name = 'products/list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        title = self.request.GET.get('title')
        variant = self.request.GET.getlist('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')
        if title:
            products = products.filter(title__icontains=title)
        if variant:
            filtered_variants = ProductVariant.objects.filter(
                variant_title__in=variant,
                product=OuterRef('pk'),
            ).values('product')
            products = products.filter(Q(pk__in=Subquery(filtered_variants)))

        if price_from and price_to:
            filtered_variants = ProductVariantPrice.objects.filter(
                price__gte=price_from,
                price__lte=price_to,
                product=OuterRef('pk'),
            ).values('product')
            products = products.filter(Q(pk__in=Subquery(filtered_variants)))

        if date:
            products = products.filter(created_at__date=date)

        page = self.request.GET.get('page')
        paginator = Paginator(products, self.paginate_by)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context['product'] = True
        context['products'] = products
        context['paginator'] = paginator

        variants = Variant.objects.filter(active=True).values('id', 'title')

        for variant in variants:
            variant['variants'] = (
                ProductVariant.objects.filter(variant_id=variant['id'])
                .values('variant_title')
                .distinct()
            )

        context['variants'] = variants
        context['selected_variants'] = self.request.GET.getlist('variant')
        return context
