# TradeNest

Multi-vendor marketplace built on Frappe/ERPNext. Customers can browse products, place orders (COD/Online), and track their orders via a Vue 3 storefront.

## Requirements

- Frappe v16
- ERPNext v16
- Node.js 18+
- Python 3.11+

## Installation

```bash
cd $YOUR_BENCH
bench get-app https://github.com/YOUR_USERNAME/trade_nest --branch version-16
bench install-app trade_nest
```

## Frontend Build

```bash
cd apps/trade_nest
npm install
npm run build
bench build --app trade_nest
```

## Configuration (site_config.json)

Razorpay keys bench ke `sites/your-site/site_config.json` mein daalo — **kabhi code mein mat daalo**:

```json
{
  "razorpay_key_id": "rzp_live_XXXXXXXXXX",
  "razorpay_key_secret": "your_secret_here"
}
```

## Custom Fields Required

`bench migrate` run karne par ye fields auto-create ho jaayenge:

- `Sales Order.custom_payment_method` — Select (COD / Online)

## Access

Storefront URL: `https://your-site/shop/`

## License

MIT
