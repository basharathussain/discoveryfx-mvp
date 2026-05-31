"""Idempotent seed of 30 fixture supplier_products for Phase-1 demo.

Runs on every api container start (no-op if products already exist).
"""
import asyncio
from decimal import Decimal

from sqlalchemy import func, select

from api.adapters.base import SupplierProductRaw
from api.adapters.normalizer import raw_to_orm
from api.db import SessionLocal
from api.models.supplier_products import SupplierProduct


FIXTURES: list[dict] = [
    # AliExpress UK source ─────────────────────────────────────────────────
    {"source": "aliexpress_uk", "title": "USB-C 65W Fast Charger Plug UK 3-Pin",
     "category": "Electronics", "external_id": "1005010100001",
     "supplier_name": "QuickPower Store",     "supplier_rating": 4.8,
     "cost_price": "5.20",  "shipping_cost": "1.40", "orders_count": 1240, "reviews_count": 340,
     "image": "https://picsum.photos/seed/ae1/300"},
    {"source": "aliexpress_uk", "title": "Bluetooth 5.3 Wireless Earbuds with ANC",
     "category": "Electronics", "external_id": "1005010100002",
     "supplier_name": "AudioTrend Direct",   "supplier_rating": 4.7,
     "cost_price": "8.40",  "shipping_cost": "0.00", "orders_count": 5430, "reviews_count": 1820,
     "image": "https://picsum.photos/seed/ae2/300"},
    {"source": "aliexpress_uk", "title": "Stainless Steel French Press Coffee Maker 1L",
     "category": "Kitchen",     "external_id": "1005010100003",
     "supplier_name": "BrewHouse Supplies",  "supplier_rating": 4.6,
     "cost_price": "6.80",  "shipping_cost": "2.10", "orders_count": 320,  "reviews_count": 84,
     "image": "https://picsum.photos/seed/ae3/300"},
    {"source": "aliexpress_uk", "title": "LED Ring Light 10\" with Tripod Stand",
     "category": "Photography", "external_id": "1005010100004",
     "supplier_name": "StreamGear Co.",      "supplier_rating": 4.5,
     "cost_price": "9.10",  "shipping_cost": "3.00", "orders_count": 870,  "reviews_count": 210,
     "image": "https://picsum.photos/seed/ae4/300"},
    {"source": "aliexpress_uk", "title": "Silicone Pet Hair Remover Brush Reusable",
     "category": "Pets",        "external_id": "1005010100005",
     "supplier_name": "PetCare Hub",         "supplier_rating": 4.7,
     "cost_price": "1.90",  "shipping_cost": "0.80", "orders_count": 2100, "reviews_count": 540,
     "image": "https://picsum.photos/seed/ae5/300"},
    {"source": "aliexpress_uk", "title": "Foldable Reusable Shopping Bags Set of 6",
     "category": "Home",        "external_id": "1005010100006",
     "supplier_name": "EcoMart Global",      "supplier_rating": 4.6,
     "cost_price": "2.30",  "shipping_cost": "0.50", "orders_count": 410,  "reviews_count": 98,
     "image": "https://picsum.photos/seed/ae6/300"},
    {"source": "aliexpress_uk", "title": "Magnetic Phone Holder for Car Dashboard",
     "category": "Automotive",  "external_id": "1005010100007",
     "supplier_name": "DriveSafe Direct",    "supplier_rating": 4.5,
     "cost_price": "3.10",  "shipping_cost": "0.00", "orders_count": 7800, "reviews_count": 2410,
     "image": "https://picsum.photos/seed/ae7/300"},
    {"source": "aliexpress_uk", "title": "Yoga Mat 6mm Non-Slip with Carry Strap",
     "category": "Fitness",     "external_id": "1005010100008",
     "supplier_name": "FlexFit Studio",      "supplier_rating": 4.6,
     "cost_price": "7.60",  "shipping_cost": "2.40", "orders_count": 240,  "reviews_count": 51,
     "image": "https://picsum.photos/seed/ae8/300"},
    {"source": "aliexpress_uk", "title": "Smart Plug Wi-Fi UK 3-Pin Energy Monitor",
     "category": "Smart Home",  "external_id": "1005010100009",
     "supplier_name": "HomeIQ Tech",         "supplier_rating": 4.7,
     "cost_price": "4.40",  "shipping_cost": "1.10", "orders_count": 1530, "reviews_count": 420,
     "image": "https://picsum.photos/seed/ae9/300"},
    {"source": "aliexpress_uk", "title": "Posture Corrector Back Brace Adjustable",
     "category": "Health",      "external_id": "1005010100010",
     "supplier_name": "WellBack Co.",        "supplier_rating": 4.4,
     "cost_price": "3.80",  "shipping_cost": "0.90", "orders_count": 920,  "reviews_count": 230,
     "image": "https://picsum.photos/seed/ae10/300"},
    {"source": "aliexpress_uk", "title": "LED Sunrise Alarm Clock Wake-Up Light",
     "category": "Home",        "external_id": "1005010100011",
     "supplier_name": "MorningGlow Lab",     "supplier_rating": 4.6,
     "cost_price": "11.20", "shipping_cost": "0.00", "orders_count": 180,  "reviews_count": 41,
     "image": "https://picsum.photos/seed/ae11/300"},
    {"source": "aliexpress_uk", "title": "Cordless Handheld Vacuum Cleaner USB-Rechargeable",
     "category": "Home",        "external_id": "1005010100012",
     "supplier_name": "PureClean Distributors", "supplier_rating": 4.5,
     "cost_price": "13.50", "shipping_cost": "2.20", "orders_count": 640,  "reviews_count": 152,
     "image": "https://picsum.photos/seed/ae12/300"},
    {"source": "aliexpress_uk", "title": "Resistance Bands Set with Door Anchor",
     "category": "Fitness",     "external_id": "1005010100013",
     "supplier_name": "PowerLine Sports",    "supplier_rating": 4.7,
     "cost_price": "4.10",  "shipping_cost": "1.30", "orders_count": 360,  "reviews_count": 88,
     "image": "https://picsum.photos/seed/ae13/300"},
    {"source": "aliexpress_uk", "title": "Anti-Snore Nasal Strips 100-Pack",
     "category": "Health",      "external_id": "1005010100014",
     "supplier_name": "SleepEasy Supply",    "supplier_rating": 4.3,
     "cost_price": "2.10",  "shipping_cost": "0.00", "orders_count": 11200, "reviews_count": 3120,
     "image": "https://picsum.photos/seed/ae14/300"},
    {"source": "aliexpress_uk", "title": "Mini Portable Sewing Machine Handheld",
     "category": "Crafts",      "external_id": "1005010100015",
     "supplier_name": "StitchPro Direct",    "supplier_rating": 4.4,
     "cost_price": "5.80",  "shipping_cost": "1.80", "orders_count": 95,   "reviews_count": 22,
     "image": "https://picsum.photos/seed/ae15/300"},

    # Amazon UK source ────────────────────────────────────────────────────
    {"source": "amazon_uk", "title": "Anker PowerCore 10000 Slim Power Bank UK",
     "category": "Electronics", "external_id": "B0AMZN0001",
     "supplier_name": "Anker UK",            "supplier_rating": 4.7,
     "cost_price": "21.99", "shipping_cost": "0.00", "orders_count": 4800, "reviews_count": 1450,
     "image": "https://picsum.photos/seed/az1/300"},
    {"source": "amazon_uk", "title": "Lifestraw Personal Water Filter Outdoor",
     "category": "Outdoors",    "external_id": "B0AMZN0002",
     "supplier_name": "LifeStraw UK",        "supplier_rating": 4.8,
     "cost_price": "14.50", "shipping_cost": "0.00", "orders_count": 2100, "reviews_count": 760,
     "image": "https://picsum.photos/seed/az2/300"},
    {"source": "amazon_uk", "title": "Philips Sonicare ProtectiveClean Toothbrush",
     "category": "Health",      "external_id": "B0AMZN0003",
     "supplier_name": "Philips UK Direct",   "supplier_rating": 4.6,
     "cost_price": "49.99", "shipping_cost": "0.00", "orders_count": 1300, "reviews_count": 410,
     "image": "https://picsum.photos/seed/az3/300"},
    {"source": "amazon_uk", "title": "Joseph Joseph Nest 9 Plus Kitchen Storage Set",
     "category": "Kitchen",     "external_id": "B0AMZN0004",
     "supplier_name": "Joseph Joseph UK",    "supplier_rating": 4.7,
     "cost_price": "32.00", "shipping_cost": "0.00", "orders_count": 880,  "reviews_count": 240,
     "image": "https://picsum.photos/seed/az4/300"},
    {"source": "amazon_uk", "title": "Govee LED Strip Lights 5m RGBIC Wi-Fi",
     "category": "Smart Home",  "external_id": "B0AMZN0005",
     "supplier_name": "Govee UK Store",      "supplier_rating": 4.5,
     "cost_price": "19.99", "shipping_cost": "0.00", "orders_count": 3400, "reviews_count": 1020,
     "image": "https://picsum.photos/seed/az5/300"},
    {"source": "amazon_uk", "title": "Hot Brush One-Step Volumiser Hair Styler",
     "category": "Beauty",      "external_id": "B0AMZN0006",
     "supplier_name": "Revlon UK",           "supplier_rating": 4.4,
     "cost_price": "29.50", "shipping_cost": "0.00", "orders_count": 5600, "reviews_count": 1850,
     "image": "https://picsum.photos/seed/az6/300"},
    {"source": "amazon_uk", "title": "Echo Dot 5th Gen Smart Speaker with Alexa",
     "category": "Smart Home",  "external_id": "B0AMZN0007",
     "supplier_name": "Amazon Devices UK",   "supplier_rating": 4.7,
     "cost_price": "34.99", "shipping_cost": "0.00", "orders_count": 18000, "reviews_count": 6200,
     "image": "https://picsum.photos/seed/az7/300"},
    {"source": "amazon_uk", "title": "Wahl Cordless Hair Clipper Kit Lithium",
     "category": "Beauty",      "external_id": "B0AMZN0008",
     "supplier_name": "Wahl UK",             "supplier_rating": 4.6,
     "cost_price": "44.00", "shipping_cost": "0.00", "orders_count": 780,  "reviews_count": 210,
     "image": "https://picsum.photos/seed/az8/300"},
    {"source": "amazon_uk", "title": "Bialetti Moka Express 6-Cup Stovetop Coffee",
     "category": "Kitchen",     "external_id": "B0AMZN0009",
     "supplier_name": "Bialetti UK",         "supplier_rating": 4.7,
     "cost_price": "23.40", "shipping_cost": "0.00", "orders_count": 1200, "reviews_count": 380,
     "image": "https://picsum.photos/seed/az9/300"},
    {"source": "amazon_uk", "title": "TP-Link Tapo Pan/Tilt Indoor Wi-Fi Camera",
     "category": "Smart Home",  "external_id": "B0AMZN0010",
     "supplier_name": "TP-Link UK",          "supplier_rating": 4.5,
     "cost_price": "21.50", "shipping_cost": "0.00", "orders_count": 2700, "reviews_count": 690,
     "image": "https://picsum.photos/seed/az10/300"},
    {"source": "amazon_uk", "title": "Brita Marella Water Filter Jug 2.4L",
     "category": "Kitchen",     "external_id": "B0AMZN0011",
     "supplier_name": "Brita UK",            "supplier_rating": 4.6,
     "cost_price": "16.99", "shipping_cost": "0.00", "orders_count": 1900, "reviews_count": 540,
     "image": "https://picsum.photos/seed/az11/300"},
    {"source": "amazon_uk", "title": "Yale Smart Lock Linus Bluetooth UK Profile",
     "category": "Smart Home",  "external_id": "B0AMZN0012",
     "supplier_name": "Yale UK",             "supplier_rating": 4.4,
     "cost_price": "169.00","shipping_cost": "0.00", "orders_count": 140,  "reviews_count": 48,
     "image": "https://picsum.photos/seed/az12/300"},
    {"source": "amazon_uk", "title": "Lakeland Microfibre Cleaning Cloths Pack of 30",
     "category": "Home",        "external_id": "B0AMZN0013",
     "supplier_name": "Lakeland UK",         "supplier_rating": 4.7,
     "cost_price": "9.99",  "shipping_cost": "0.00", "orders_count": 320,  "reviews_count": 90,
     "image": "https://picsum.photos/seed/az13/300"},
    {"source": "amazon_uk", "title": "FoxTail Outdoor Bird Feeder Squirrel-Proof",
     "category": "Garden",      "external_id": "B0AMZN0014",
     "supplier_name": "FoxTail Outdoors",    "supplier_rating": 4.5,
     "cost_price": "27.00", "shipping_cost": "0.00", "orders_count": 60,   "reviews_count": 14,
     "image": "https://picsum.photos/seed/az14/300"},
    {"source": "amazon_uk", "title": "Crayola Ultimate Crayon Collection 152-Pack",
     "category": "Kids",        "external_id": "B0AMZN0015",
     "supplier_name": "Crayola UK",          "supplier_rating": 4.8,
     "cost_price": "18.50", "shipping_cost": "0.00", "orders_count": 970,  "reviews_count": 305,
     "image": "https://picsum.photos/seed/az15/300"},
]


async def seed() -> None:
    async with SessionLocal() as db:
        existing = (await db.execute(select(func.count(SupplierProduct.id)))).scalar_one()
        if existing >= len(FIXTURES):
            print(f"[seed] {existing} products already present, skipping.")
            return

        rows = []
        for f in FIXTURES:
            raw = SupplierProductRaw(
                source=f["source"],
                supplier_name=f["supplier_name"],
                supplier_rating=f["supplier_rating"],
                product_url=f"https://example.invalid/seed/{f['source']}/{f['external_id']}",
                external_id=f["external_id"],
                title=f["title"],
                image=f["image"],
                category=f["category"],
                currency="GBP",
                cost_price=Decimal(f["cost_price"]),
                shipping_cost=Decimal(f["shipping_cost"]),
                orders_count=f["orders_count"],
                reviews_count=f["reviews_count"],
            )
            rows.append(raw_to_orm(raw))

        db.add_all(rows)
        await db.commit()
        print(f"[seed] inserted {len(rows)} fixture products.")


if __name__ == "__main__":
    asyncio.run(seed())
