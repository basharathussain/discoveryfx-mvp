"""Re-export every model so that importing any of them registers all
tables on Base.metadata. Avoids 'could not find table X' FK errors when
a script only imports one model directly."""
from api.models.users import User  # noqa: F401
from api.models.supplier_products import SupplierProduct  # noqa: F401
from api.models.stores import Store  # noqa: F401
from api.models.listings import Listing  # noqa: F401
from api.models.orders import Order  # noqa: F401
from api.models.markup_rules import MarkupRule  # noqa: F401
