"""Heuristic scoring engine. All scores are 0..100 floats. Each function returns
(score, inputs_dict) so the value is explainable in the UI."""
from decimal import Decimal
from typing import Tuple


# --- Sub-scores -------------------------------------------------------------

def trend_score(orders_count: int, reviews_count: int) -> Tuple[float, dict]:
    """Higher orders + reviews → higher trend signal, log-shaped (so 5k orders ≠ 5× 1k)."""
    import math
    o = max(orders_count or 0, 0)
    r = max(reviews_count or 0, 0)
    raw = math.log10(o + 1) * 25 + math.log10(r + 1) * 15
    score = max(0.0, min(100.0, raw))
    return score, {"orders_count": o, "reviews_count": r, "formula": "log10(o+1)*25 + log10(r+1)*15"}


def supplier_score(rating: float | None, reviews_count: int) -> Tuple[float, dict]:
    """Combines rating (out of 5) with review count (volume = confidence)."""
    import math
    rating = float(rating) if rating is not None else 0.0
    rev = max(reviews_count or 0, 0)
    rating_pts = (rating / 5.0) * 70.0
    volume_pts = min(math.log10(rev + 1) * 10.0, 30.0)
    score = max(0.0, min(100.0, rating_pts + volume_pts))
    return score, {"rating": rating, "reviews_count": rev,
                   "rating_pts": round(rating_pts, 2), "volume_pts": round(volume_pts, 2)}


def margin_score(cost_price: Decimal, shipping_cost: Decimal, suggested_sell: Decimal | None = None,
                 default_markup_pct: Decimal = Decimal("35")) -> Tuple[float, dict]:
    """Score based on margin headroom. If suggested_sell missing, derives from default markup."""
    landed = (cost_price or Decimal(0)) + (shipping_cost or Decimal(0))
    if landed <= 0:
        return 0.0, {"reason": "no_cost"}
    sell = suggested_sell or (landed * (Decimal(1) + default_markup_pct / Decimal(100)))
    margin_abs = sell - landed
    margin_pct = float(margin_abs / landed) * 100.0
    # 0% → 0, 30% → 60, 50%+ → 90+
    raw = margin_pct * 1.8
    score = max(0.0, min(100.0, raw))
    return score, {"landed_cost": float(landed), "suggested_sell": float(sell),
                   "margin_pct": round(margin_pct, 2)}


def competition_score(orders_count: int) -> Tuple[float, dict]:
    """Inverse-ish: too few orders = unproven; too many = crowded. Sweet spot ~ 100–500 orders."""
    o = max(orders_count or 0, 0)
    if o < 20:        raw = 30.0
    elif o < 100:     raw = 70.0
    elif o < 500:     raw = 90.0
    elif o < 2000:    raw = 65.0
    elif o < 10000:   raw = 40.0
    else:             raw = 20.0
    return raw, {"orders_count": o, "bucket": _bucket(o)}


def _bucket(o: int) -> str:
    if o < 20: return "unproven"
    if o < 100: return "early"
    if o < 500: return "sweet_spot"
    if o < 2000: return "established"
    if o < 10000: return "crowded"
    return "saturated"


# --- Overall ---------------------------------------------------------------

# Weights are explicit so they can be tuned without a code change later.
WEIGHTS = {
    "trend":       0.35,
    "margin":      0.30,
    "supplier":    0.20,
    "competition": 0.15,
}


def overall_score(trend: float, supplier: float, margin: float, competition: float) -> Tuple[float, dict]:
    raw = (
        trend       * WEIGHTS["trend"]
        + margin    * WEIGHTS["margin"]
        + supplier  * WEIGHTS["supplier"]
        + competition * WEIGHTS["competition"]
    )
    return round(raw, 2), {**WEIGHTS, "components": {
        "trend": trend, "margin": margin, "supplier": supplier, "competition": competition,
    }}


def score_supplier_product(*, cost_price, shipping_cost, orders_count, reviews_count,
                           supplier_rating) -> dict:
    """One-call helper used by adapters + seed. Returns a dict ready to splat into the ORM row."""
    t, t_in = trend_score(orders_count, reviews_count)
    s, s_in = supplier_score(supplier_rating, reviews_count)
    m, m_in = margin_score(cost_price, shipping_cost)
    c, c_in = competition_score(orders_count)
    o, o_in = overall_score(t, s, m, c)
    return {
        "trend_score": t, "trend_inputs": t_in,
        "supplier_score": s, "supplier_inputs": s_in,
        "margin_score": m, "margin_inputs": m_in,
        "competition_score": c, "competition_inputs": c_in,
        "overall_score": o, "overall_inputs": o_in,
    }
