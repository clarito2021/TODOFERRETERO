# pdf_pedido.py
# Genera un PDF de Pedido a partir del order_no.
# 2025-09-04 - TODO FERRETERO - Chatcito

import os, sqlite3, datetime, locale
from pathlib import Path
from kivy.utils import platform

# --- Import condicional de jnius (solo en Android) ---
# Evita advertencias en VS Code / Pylance cuando trabajas en macOS/Windows.
_autoclass = None
if platform == "android":
    try:
        from jnius import autoclass as _autoclass  # type: ignore[import-not-found]
    except Exception:
        _autoclass = None

# Ajusta separadores miles con locale; si falla, usamos un formateador simple
try:
    locale.setlocale(locale.LC_ALL, "es_CL.UTF-8")
except Exception:
    pass

def miles(n):
    try:
        s = locale.format_string("%d", int(n), grouping=True)
        return s.replace(",", ".")
    except Exception:
        return f"{int(n):,}".replace(",", ".")

# --- Rutas básicas (funcionan tanto en desktop como en Android) ---
_BASE_DIR = Path(__file__).parent

def _db_path() -> str:
    return str(_BASE_DIR / "bd_sqlite" / "todoferre.db")

def _logo_path() -> str:
    return str(_BASE_DIR / "images" / "logo-todo-ferretero.jpg")

def _safe_exports_dir() -> Path:
    """Directorio donde escribir PDFs.
       - Android: app/files privada (no requiere permisos)
       - Otros: carpeta local 'exports'
    """
    if platform == "android":
        try:
            if _autoclass is None:
                raise RuntimeError("JNI no disponible")
            PythonActivity = _autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            fdir = activity.getExternalFilesDir(None) or activity.getFilesDir()
            return Path(fdir.getAbsolutePath())
        except Exception:
            # Último recurso: junto al .py (no ideal en Android, pero evita fallos)
            return _BASE_DIR / "exports"
    else:
        return _BASE_DIR / "exports"

def _fetch_order(con, order_no):
    cur = con.cursor()
    cur.execute("""
        SELECT order_no, user, cliente_rowid, cliente_display, mode, region,
               subtotal, iva, total, created_at,
               cliente_rut, cliente_direccion, cliente_comuna, cliente_ciudad,
               cliente_estado, cliente_email, forma_pago, direccion_despacho,
               realizado_por_usuario, realizado_por_nombre
        FROM orders
        WHERE order_no = ?
        LIMIT 1
    """, (order_no,))
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"No existe order_no='{order_no}' en orders")
    keys = ["order_no","user","cliente_rowid","cliente_display","mode","region",
            "subtotal","iva","total","created_at",
            "cliente_rut","cliente_direccion","cliente_comuna","cliente_ciudad",
            "cliente_estado","cliente_email","forma_pago","direccion_despacho",
            "realizado_por_usuario","realizado_por_nombre"]
    return dict(zip(keys, row))

def _fetch_items(con, order_no):
    cur = con.cursor()
    cur.execute("""
        SELECT sku, product, marca, categoria, unit_price, qty, total
        FROM detalle_productos_orden
        WHERE order_no = ?
        ORDER BY id
    """, (order_no,))
    items = []
    for sku, product, marca, categoria, unit_price, qty, total in cur.fetchall():
        items.append({
            "sku": sku or "",
            "product": (product or "").strip(),
            "marca": (marca or "") or "",
            "unit_price": int(unit_price or 0),
            "qty": int(qty or 0),
            "total": int(total or 0),
            "dscto_pct": 0,
        })
    return items

def export_order_pdf(order_no, out_dir: str | Path | None = None):
    """Genera el PDF para un order_no y devuelve la ruta del archivo.
       Si ReportLab no está disponible en el APK, levanta una excepción clara.
    """
    # --- IMPORT LAZY de reportlab (para no romper el arranque en Android si no está incluido) ---
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
    except Exception as e:
        raise RuntimeError("ReportLab no está instalado en este build. "
                           "Vuelva a compilar el APK incluyendo 'reportlab' en requirements "
                           "o genere el PDF desde el PC.") from e

    # Carpeta de salida segura
    out_base = Path(out_dir) if out_dir else _safe_exports_dir()
    out_base.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(_db_path())
    try:
        o = _fetch_order(con, order_no)
        items = _fetch_items(con, order_no)
    finally:
        con.close()

    fecha_str = datetime.datetime.fromtimestamp(int(o["created_at"])).strftime("%Y-%m-%d %H:%M")

    out_path = out_base / f"Pedido_{order_no}.pdf"
    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=14*mm, bottomMargin=14*mm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleRight", parent=styles["Heading1"], alignment=2))
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=9, leading=11))
    styles.add(ParagraphStyle(name="SmallBold", parent=styles["Normal"], fontSize=9, leading=11, spaceAfter=0))
    styles.add(ParagraphStyle(name="Header", parent=styles["Normal"], fontSize=10, leading=12))

    flow = []

    # Encabezado: logo + título
    logo_file = _logo_path()
    logo_w = 35*mm
    if Path(logo_file).exists():
        logo = Image(logo_file, width=logo_w, height=logo_w*0.75)
    else:
        logo = Spacer(logo_w, 20)
    titulo = Paragraph("Pedido", styles["TitleRight"])
    head_tbl = Table([[logo, titulo]], colWidths=[logo_w, 150*mm - logo_w])
    head_tbl.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                  ("ALIGN",(1,0),(1,0),"RIGHT"),
                                  ("BOX",(0,0),(-1,-1),0,colors.white)]))
    flow += [head_tbl, Spacer(1, 6)]

    # Fecha / N° Orden / Realizado por
    linea = Table([[
        Paragraph(f"<b>Fecha:</b> {fecha_str}", styles["Header"]),
        Paragraph(f"<b>Num. Órden:</b> {o['order_no']}", styles["Header"]),
        Paragraph(f"<b>Realizado por:</b> {o['realizado_por_nombre'] or o['realizado_por_usuario']}", styles["Header"])
    ]], colWidths=[60*mm, 55*mm, 65*mm])
    flow += [linea, Spacer(1, 8)]

    # Datos cliente (borde negro)
    c_left = [
        Paragraph(f"<b>Señor(es):</b> {o['cliente_display'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Dirección:</b> {o['cliente_direccion'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Forma de Pago:</b> {o['forma_pago'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Dirección de Despacho:</b> {o['direccion_despacho'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Lista de Precios:</b> {o['region'] or '—'}", styles["Small"]),
    ]
    c_right = [
        Paragraph(f"<b>RUT:</b> {o['cliente_rut'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Comuna:</b> {o['cliente_comuna'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Ciudad:</b> {o['cliente_ciudad'] or '—'}", styles["Small"]),
        Paragraph(f"<b>Email:</b> {o['cliente_email'] or '—'}", styles["Small"]),
        Paragraph("", styles["Small"]),
    ]
    cli_tbl = Table([[c_left, c_right]], colWidths=[100*mm, 80*mm])
    from reportlab.lib import colors as _colors
    from reportlab.platypus import TableStyle as _TableStyle
    cli_tbl.setStyle(_TableStyle([
        ("BOX",(0,0),(-1,-1), 1, _colors.black),
        ("VALIGN",(0,0),(-1,-1), "TOP"),
        ("INNERGRID",(0,0),(-1,-1), 0, _colors.white),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("RIGHTPADDING",(0,0),(-1,-1), 6),
        ("TOPPADDING",(0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ]))
    flow += [cli_tbl, Spacer(1, 10)]

    # Ítems
    headers = ["Código", "Descripción", "Marca", "Cant.", "Precio Neto", "Dscto.(%)", "Total Neto"]
    data = [headers]
    for it in items:
        data.append([
            it["sku"],
            Paragraph((it["product"] or "—"), styles["Small"]),
            Paragraph((it["marca"] or "—"), styles["Small"]),
            str(it["qty"]),
            f"${miles(it['unit_price'])}",
            f"{it['dscto_pct']}%",
            f"${miles(it['total'])}",
        ])

    items_tbl = Table(
        data,
        colWidths=[26*mm, 74*mm, 22*mm, 16*mm, 26*mm, 18*mm, 28*mm]
    )
    items_tbl.setStyle(_TableStyle([
        ("BOX",(0,0),(-1,-1), 1, _colors.black),
        ("GRID",(0,0),(-1,-1), 0.25, _colors.grey),
        ("BACKGROUND",(0,0),(-1,0), _colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",(3,1),(3,-1), "RIGHT"),
        ("ALIGN",(4,1),(-1,-1), "RIGHT"),
        ("FONTNAME",(0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 9),
        ("LEFTPADDING",(0,0),(-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1), 4),
        ("TOPPADDING",(0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]))
    flow += [items_tbl]

    # Totales
    resumen = Table([
        [Paragraph("<b>Total Neto:</b>", styles["Small"]),  Paragraph(f"${miles(o['subtotal'])}", styles["Small"])],
        [Paragraph("<b>IVA (19%):</b>", styles["Small"]),   Paragraph(f"${miles(o['iva'])}", styles["Small"])],
        [Paragraph("<b>Total:</b>", styles["SmallBold"]),   Paragraph(f"${miles(o['total'])}", styles["SmallBold"])],
    ], colWidths=[30*mm, 30*mm])
    resumen.setStyle(_TableStyle([
        ("ALIGN",(0,0),(0,-1), "RIGHT"),
        ("ALIGN",(1,0),(1,-1), "RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1), 2),
    ]))
    flow += [Spacer(1, 8), Table([[Spacer(1,1), resumen]], colWidths=[130*mm, 60*mm],
                                 style=_TableStyle([("BOX",(0,0),(-1,-1),0,_colors.white)]))]

    doc.build(flow)
    return str(out_path)

if __name__ == "__main__":
    pass
