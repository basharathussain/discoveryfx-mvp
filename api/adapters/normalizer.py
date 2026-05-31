"""Maps SupplierProductRaw → ORM SupplierProduct row, applying scoring."""
from decimal import Decimal

from api.adapters.base import SupplierProductRaw
from api.models.supplier_products import SupplierProduct
from api.scoring.engine import score_supplier_product


def raw_to_orm(raw: SupplierProductRaw) -> SupplierProduct:
    scores = score_supplier_product(
        cost_price=raw.cost_price,
        shipping_cost=raw.shipping_cost,
        orders_count=raw.orders_count,
        reviews_count=raw.reviews_count,
        supplier_rating=raw.supplier_rating,
    )
    return SupplierProduct(
        source=raw.source,
        supplier_name=raw.supplier_name,
        supplier_rating=raw.supplier_rating,
        product_url=raw.product_url,
        external_id=raw.external_id,
        title=raw.title,
        image=raw.image,
        category=raw.category,
        currency=raw.currency or "GBP",
        cost_price=Decimal(raw.cost_price),
        shipping_cost=Decimal(raw.shipping_cost or 0),
        orders_count=raw.orders_count or 0,
        reviews_count=raw.reviews_count or 0,
        **scores,
    )
