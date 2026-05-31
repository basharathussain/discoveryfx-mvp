"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "supplier_products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("supplier_name", sa.String(255), nullable=False),
        sa.Column("supplier_rating", sa.Float, nullable=True),
        sa.Column("product_url", sa.Text, nullable=False),
        sa.Column("external_id", sa.String(64), nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="GBP"),
        sa.Column("cost_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("shipping_cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("orders_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reviews_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("trend_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("trend_inputs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("supplier_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("supplier_inputs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("margin_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("margin_inputs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("competition_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("competition_inputs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("overall_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("overall_inputs", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("discovered_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_supplier_products_source", "supplier_products", ["source"])
    op.create_index("ix_supplier_products_external_id", "supplier_products", ["external_id"])
    op.create_index("ix_supplier_products_category", "supplier_products", ["category"])
    op.create_index("ix_supplier_products_overall_score", "supplier_products", ["overall_score"])

    op.create_table(
        "stores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", sa.String(32), nullable=False, server_default="ebay"),
        sa.Column("store_name", sa.String(255), nullable=False),
        sa.Column("region", sa.String(8), nullable=False, server_default="GB"),
        sa.Column("access_token", sa.Text, nullable=True),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="connected"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_stores_user_id", "stores", ["user_id"])

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("supplier_product_id", sa.Integer, sa.ForeignKey("supplier_products.id"), nullable=False),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("currency", sa.String(3), nullable=False, server_default="GBP"),
        sa.Column("selling_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("profit_margin", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("ebay_item_id", sa.String(64), nullable=True),
        sa.Column("ebay_offer_id", sa.String(64), nullable=True),
        sa.Column("ebay_sku", sa.String(64), nullable=True),
        sa.Column("publish_error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_listings_user_id", "listings", ["user_id"])
    op.create_index("ix_listings_supplier_product_id", "listings", ["supplier_product_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("listing_id", sa.Integer, sa.ForeignKey("listings.id"), nullable=True),
        sa.Column("ebay_order_id", sa.String(64), nullable=False),
        sa.Column("buyer_name", sa.String(255), nullable=True),
        sa.Column("buyer_email", sa.String(255), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="GBP"),
        sa.Column("total", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("supplier_product_url", sa.Text, nullable=True),
        sa.Column("order_status", sa.String(32), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_orders_store_id", "orders", ["store_id"])
    op.create_index("ix_orders_listing_id", "orders", ["listing_id"])
    op.create_index("ix_orders_ebay_order_id", "orders", ["ebay_order_id"])

    op.create_table(
        "markup_rules",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("default_markup_pct", sa.Numeric(5, 2), nullable=False, server_default="35.00"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="GBP"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_markup_rules_user_id", "markup_rules", ["user_id"])


def downgrade() -> None:
    op.drop_table("markup_rules")
    op.drop_table("orders")
    op.drop_table("listings")
    op.drop_table("stores")
    op.drop_table("supplier_products")
    op.drop_table("users")
