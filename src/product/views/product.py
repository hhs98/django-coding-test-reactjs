from django.views import generic
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, OuterRef, Q
from product.models import (
    Variant,
    Product,
    ProductVariant,
    ProductVariantPrice,
)


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


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
