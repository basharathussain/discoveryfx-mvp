# DiscoveryFX — Phase 1 vertical demo

UK-first dropshipping product-discovery MVP.
**Status:** Phase 1 (skeleton + seeded discovery + draft listings) is live end-to-end.
**Pending:** Phase 2 (live AliExpress UK + Amazon UK scraping) and Phase 3 (eBay Sandbox publish).

---

## What works right now

| Layer | Status |
|---|---|
| 5-service Docker stack (api, worker, web, postgres, redis) | ✅ |
| Email/password signup + login (argon2 + JWT) | ✅ |
| 6-table schema with Alembic migration | ✅ |
| 30 seeded UK supplier products (mix of AliExpress UK + Amazon UK) | ✅ |
| Heuristic scoring engine (trend/margin/supplier/competition → overall) with explainable inputs | ✅ |
| Adapter contract (`SupplierAdapter` Protocol) + stubs for both sources | ✅ |
| Discovery UI: AG Grid + filters + sortable score columns + detail drawer | ✅ |
| Create-draft-listing flow from Discovery | ✅ |
| Listings page with draft/active/failed sections | ✅ |
| Settings: default markup % (drives suggested sell price) | ✅ |
| Store integrations placeholder (eBay UK stub store creation) | ✅ |
| **eBay OAuth + Inventory/Offer/Publish** | ⏳ Phase 3 — stub returns 501 |
| **Live scraping** (AliExpress UK & Amazon UK) | ⏳ Phase 2 — adapters raise `NotImplementedError` |

---

## Run it

```bash
cd _src
docker compose up -d --build
```

Then visit:

- Web app: <http://localhost:3001>
- API docs: <http://localhost:8081/docs>
- Health: <http://localhost:8081/api/health>

Sign up with any email/password (min 8 chars). The Discovery page loads the 30 seeded
products sorted by overall score. Click any row to see the detail drawer with score
inputs, then "Create draft listing" to push a row into the Listings page.

A demo user already exists from smoke testing:
- Email: `demo@example.com`
- Password: `demopass123`

To reset state and start clean:

```bash
docker compose down -v
docker compose up -d --build
```

---

## Architecture

```
            ┌─────────────┐
            │  web (nginx)│   localhost:3001  ─── proxies /api/* ──┐
            └─────────────┘                                         │
                                                                    ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │   api (FastAPI)─────┤   postgres    │      │     redis     │
            │   port 8081  │      │   port 5440  │      │   (internal)  │
            └──────────────┘      └──────────────┘      └──────────────┘
                  │                                            ▲
                  └────► worker (RQ, idle in Phase 1) ─────────┘
```

- All Python in `api/`, all TS/React in `web/`
- One source of truth for env vars: `.env` at the project root (compose loads it for api+worker)
- Project name pinned to `discoveryfx` in compose so volumes don't collide with sibling projects

### Backend layout

```
api/
├── main.py              # FastAPI app + router mounts + /api/health
├── config.py            # Pydantic-settings, all env-driven
├── db.py                # async engine + session
├── seed.py              # idempotent fixture loader (runs at api boot)
├── models/              # 6 SQLAlchemy 2 typed models, one per file
├── schemas/             # Pydantic in/out DTOs
├── routers/             # /auth /products /listings /stores /orders /settings
├── auth/                # password (argon2), jwt, current_user dep
├── adapters/
│   ├── base.py          # SupplierAdapter Protocol + SupplierProductRaw DTO
│   ├── aliexpress_uk.py # Phase 2 stub
│   ├── amazon_uk.py     # Phase 2 stub
│   └── normalizer.py    # raw DTO → ORM row, applies scoring
├── scoring/engine.py    # heuristic scores, weights are explicit + tunable
└── workers/worker.py    # RQ entry, idle in Phase 1
```

### Frontend layout

```
web/src/
├── main.tsx, App.tsx
├── stores/authStore.ts        # zustand, persisted to localStorage
├── api/client.ts              # axios + auth interceptor + 401 redirect
├── api/hooks.ts               # all React-Query hooks
├── components/AppShell.tsx    # sidebar + topbar layout
├── pages/Login.tsx, Signup.tsx
├── pages/Dashboard.tsx        # counts of products / drafts / active
├── pages/Discovery.tsx        # AG Grid + filters + detail drawer + Create Listing
├── pages/Listings.tsx         # drafts / active / failed sections
├── pages/Orders.tsx, Stores.tsx, Settings.tsx
└── types.ts
```

---

## How to advance to Phase 2 (real scraping)

1. **AliExpress UK** — fill `api/adapters/aliexpress_uk.py`. Use `curl_cffi` with the `GB_COOKIE` constant already on the class; fall back to Playwright when SSR markers are missing. Mark `currency = "GBP"` and parse the price field labelled in £.
2. **Amazon UK** — fill `api/adapters/amazon_uk.py`. Hit `amazon.co.uk` with `curl_cffi`, parse ASIN from URL, parse listing details from the product page.
3. Add an RQ job in `api/workers/scrape_jobs.py` that calls each adapter's `search()` and writes rows via `normalizer.raw_to_orm`.
4. Wire a queue trigger (cron or on-demand) from a new `/api/products/scrape` route.

The adapter contract is the line: **no per-source field handling outside its adapter module.**
If a future change makes you reach for a supplier check elsewhere in the codebase, the
adapter shape is wrong — fix the adapter, not the consumer.

## How to advance to Phase 3 (eBay Sandbox publish)

1. Register at <https://developer.ebay.com>, create a Sandbox keyset.
2. Put credentials in `.env`:
   ```
   EBAY_CLIENT_ID=YourSandboxAppID
   EBAY_CLIENT_SECRET=YourSandboxCertID
   EBAY_REDIRECT_URI=http://localhost:8081/api/stores/ebay/callback
   ```
3. Implement `api/routers/stores.py` `ebay_connect_start()` (redirect to eBay consent URL) and `ebay_callback()` (exchange `code` for tokens, persist on `stores`).
4. Implement `api/ebay/client.py`:
   - `create_inventory_item(sku, listing)` → Inventory API
   - `create_offer(sku, listing, store)` → Offer API
   - `publish_offer(offer_id)` → Publish Offer API
5. Wire `api/routers/listings.py::publish_listing` to call those three in sequence and
   store `ebay_item_id` + `ebay_offer_id` + `ebay_sku` on the listing row.
6. `EBAY_ENV=sandbox` until three successful publishes in a row; only then flip to `prod`.

The publish endpoint already exists as a stub at `POST /api/listings/{id}/publish` and
returns 501 with a clear message until credentials are configured.

---

## Key design rules (do not break these)

- **Supplier product = unit of opportunity.** No dedup across sources, even for "the same" item.
- **All money is `Numeric(10,2)`** — never float. GBP everywhere in MVP.
- **Every score writes its `_inputs` JSONB** in the same transaction. The UI surfaces them so users can see *why* a score is what it is.
- **Adapters are sealed.** No per-source `if source == "amazon_uk":` anywhere outside `api/adapters/amazon_uk.py`.
- **Every router function depends on `current_user`** except `/auth/signup` and `/auth/login`.
- **`EBAY_ENV=sandbox`** by default. Production credentials only after sandbox publishes are reliable.

---

## Tests / verification

Manual smoke test (already passes):

```bash
# health
curl http://localhost:8081/api/health

# signup
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"testpass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# products
curl -s "http://localhost:8081/api/products?page=1&page_size=3" \
  -H "Authorization: Bearer $TOKEN"

# create draft listing
curl -s -X POST http://localhost:8081/api/listings \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"supplier_product_id":1}'
```

Automated tests for the scoring engine + auth happy path are planned for Phase 4.
