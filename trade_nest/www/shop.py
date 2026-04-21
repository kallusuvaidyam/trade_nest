import frappe
from pathlib import Path

no_cache = 1


def get_context(context):
    # Auth Vue SPA handle karti hai via router guard — server-side redirect nahi
    build_index = (
        Path(frappe.get_app_path("trade_nest"))
        / "public"
        / "shop"
        / "index.html"
    )

    if not build_index.exists():
        context.vite_head_html = ""
        context.vite_body_html = '<div id="app"></div>'
        return

    html = build_index.read_text(encoding="utf-8")

    head_start = html.find("<head>")
    head_end = html.find("</head>")
    body_start = html.find("<body>")
    body_end = html.find("</body>")

    head_inner = ""
    body_inner = '<div id="app"></div>'

    if head_start != -1 and head_end != -1:
        head_inner = html[head_start + len("<head>") : head_end].strip()

    if body_start != -1 and body_end != -1:
        body_inner = html[body_start + len("<body>") : body_end].strip()

    context.vite_head_html = head_inner
    context.vite_body_html = body_inner
