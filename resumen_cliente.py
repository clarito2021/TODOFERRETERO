# resumen_cliente.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import os, sqlite3, json, time

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.app import App

# ---- BD ----
DB_PATH = Path("bd_sqlite/todoferre.db").expanduser().resolve()

# Campos que traemos (puedes ampliar)
_FIELDS = [
    "direccion_completa",
    "terminos_de_pago_del_cliente",
    "comuna",
    "ciudad",
    "estado",
    "vendedor",
    "correo_electronico",
    "numero_identificacion_fiscal",
    "nombre_fantasia",
    "nombre_completo",
]

# Regiones visibles cuando haya que elegir manualmente
REGIONES_PERMITIDAS = [
    "Chiloe (CL)", "Coquimbo (CL)", "de la Araucania (CL)", "de los Lagos (CL)",
    "del BíoBio (CL)", "del Libertador Gral. Bernardo O'Higgins (CL)",
    "del Maule (CL)", "del Ñuble (CL)", "Metropolitana (CL)", "Valparaíso (CL)",
]

# ---------- helpers BD ----------
def _ensure_order_tables():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS order_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        cliente_rowid INTEGER NOT NULL,
        payload_json TEXT NOT NULL,
        updated_at INTEGER NOT NULL,
        UNIQUE(user, cliente_rowid)
      )
    """)
    con.commit(); con.close()

def draft_exists(user: str, cliente_rowid: int) -> bool:
    _ensure_order_tables()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT 1 FROM order_drafts WHERE user=? AND cliente_rowid=? LIMIT 1",
        (user, cliente_rowid),
    )
    ok = cur.fetchone() is not None
    con.close()
    return ok

def _fetch_full_client(selected: Dict[str, Any]) -> Dict[str, str]:
    """Busca un cliente por rowid (preferido) o por nombre."""
    empty = {k: "—" for k in _FIELDS}
    if not DB_PATH.exists():
        return empty

    cid = selected.get("cliente_id")
    nf = (selected.get("nombre_fantasia") or "").strip()
    nc = (selected.get("nombre_completo") or "").strip()

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        if cid:
            cur.execute(f"SELECT {', '.join(_FIELDS)} FROM clientes WHERE rowid=? LIMIT 1", (cid,))
        else:
            cur.execute(f"""
                SELECT {", ".join(_FIELDS)}
                FROM clientes
                WHERE (LOWER(nombre_fantasia)=LOWER(?) AND ?<> '')
                   OR (LOWER(nombre_completo)=LOWER(?) AND ?<> '')
                LIMIT 1
            """, (nf, nf, nc, nc))
        row = cur.fetchone()
        if not row:
            return empty
        return {k: (row[k] if row[k] not in (None, "") else "—") for k in _FIELDS}
    except Exception as e:
        print("[RESUMEN][DB][ERROR]", e)
        return empty
    finally:
        con.close()


# ================== PANTALLA ==================
class ClientSummaryScreen(Screen):
    """Resumen del cliente + selección de modalidad de precios/envío."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Estado UI / contexto para carrito
        self._selected: Optional[Dict[str, Any]] = None
        self._full: Dict[str, str] = {}
        self._cliente_rowid: Optional[int] = None
        self._cliente_estado: Optional[str] = None
        self.shipping_mode: Optional[str] = None     # "retiro" | "despacho"
        self.price_region: Optional[str] = None      # región efectiva de precios
        self._current_user = getattr(App.get_running_app(), "current_user", "usuario")

        # ---- layout raíz ----
        root = BoxLayout(orientation="vertical", padding=24, spacing=16)
        self.root_box = root  # por si luego quieres añadir dinámicamente

        # Título
        self.title = Label(
            markup=True, halign="left", valign="top",
            font_size=22, size_hint=(1, None), height=dp(72), color=(1,1,1,1),
        )
        self.title.bind(size=lambda *_: setattr(self.title, "text_size", (self.title.width, None)))
        root.add_widget(self.title)

        # Bloque info alineado
        self.info_scroll = ScrollView(size_hint=(1, 0.52), do_scroll_x=False)
        self.info_grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(6), padding=[0,0,0,dp(6)])
        self.info_grid.bind(minimum_height=self.info_grid.setter("height"))
        self.info_scroll.add_widget(self.info_grid)
        root.add_widget(self.info_scroll)

        # ---------- Selector de modalidad (OBLIGATORIO) ----------
        self.selector_box = BoxLayout(orientation="vertical", size_hint=(1, None), padding=[0, dp(4), 0, 0])
        self.selector_box.bind(minimum_height=self.selector_box.setter("height"))

        selector_title = Label(
            text="Se debe seleccionar una opción de despacho…",
            size_hint=(1, None), height=28, color=(1,1,1,1)
        )

        self.shipping_spinner = Spinner(
            text="Seleccione…",
            values=("Retiro en Tienda", "Despacho"),
            size_hint=(1, None), height=44
        )

        # Región (visible sólo si corresponde)
        self.region_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=44)
        self.region_label = Label(text="[b]Región:[/b]", markup=True,
                                  size_hint=(0.28, 1), halign="right", valign="middle", color=(1,1,1,1))
        self.region_label.bind(size=lambda *_: setattr(self.region_label, "text_size", self.region_label.size))
        self.region_spinner = Spinner(
            text="Seleccione región…",
            values=tuple(REGIONES_PERMITIDAS),
            size_hint=(0.72, 1)
        )
        self.region_row.add_widget(self.region_label)
        self.region_row.add_widget(self.region_spinner)
        self.region_row.opacity = 0
        self.region_row.disabled = True

        # Botón persistente para retomar (oculto por defecto)
        self._retomar_btn = Button(
            text="Retomar pedido guardado",
            size_hint=(1, None),
            height=46,
            opacity=0,
            disabled=True,
        )

        # Montamos el bloque del selector
        self.selector_box.add_widget(selector_title)
        self.selector_box.add_widget(self.shipping_spinner)
        self.selector_box.add_widget(self.region_row)
        self.selector_box.add_widget(self._retomar_btn)
        root.add_widget(self.selector_box)

        # Notas (hint negro)
        self.notes = TextInput(
            hint_text="Notas (opcional)…",
            multiline=True,
            size_hint=(1, 0.20),
            hint_text_color=(0, 0, 0, 1),    # placeholder negro
            foreground_color=(1, 1, 1, 1),   # texto del usuario en blanco
            cursor_color=(1, 1, 1, 1),
        )
        root.add_widget(self.notes)

        # Botonera
        btns = BoxLayout(orientation="horizontal", spacing=12, size_hint=(1, 0.15))
        back_btn = Button(text="< Volver a la búsqueda")
        self.next_btn = Button(text="Siguiente >", disabled=True)
        back_btn.bind(on_release=self._back)
        self.next_btn.bind(on_release=self._continue)
        btns.add_widget(back_btn)
        btns.add_widget(self.next_btn)
        root.add_widget(btns)

        # --- Lógica del selector ---
        def _refresh_next_enabled():
            ok = self.shipping_mode in ("retiro", "despacho")
            if self.shipping_mode == "despacho" and (self._cliente_estado in (None, "", "—", "-", "NULL", "None")):
                ok = ok and bool(self.price_region)
            self.next_btn.disabled = not ok

        def _on_shipping_select(_sp, value):
            if value == "Retiro en Tienda":
                self.shipping_mode = "retiro"
                self.price_region = "Metropolitana (CL)"
                self.region_row.opacity = 0
                self.region_row.disabled = True
            else:
                self.shipping_mode = "despacho"
                if self._cliente_estado and str(self._cliente_estado).strip() not in ("", "—", "-", "NULL", "None"):
                    self.price_region = self._cliente_estado
                    self.region_row.opacity = 0
                    self.region_row.disabled = True
                else:
                    self.price_region = None
                    self.region_row.opacity = 1
                    self.region_row.disabled = False
            _refresh_next_enabled()

        def _on_region_select(_sp, value):
            if self.shipping_mode == "despacho":
                self.price_region = value
            _refresh_next_enabled()

        self.shipping_spinner.bind(text=_on_shipping_select)
        self.region_spinner.bind(text=_on_region_select)
        _refresh_next_enabled()

        # montar todo
        self.add_widget(root)

    # ---------- Acción: retomar ----------
    def _go_retomar(self, *_):
        app = App.get_running_app()
        app.order_ctx = {
            "mode": None,            # lo toma carrito desde el borrador
            "region": None,
            "cliente_rowid": self._cliente_rowid,
            "cliente_display": self.title.text.replace("Resumen de cliente:\n", ""),
            "notes": self.notes.text,
            "from_draft": True,
        }
        self._continue(None)

    # ---------- Render filas alineadas ----------
    def _render_info(self, data: Dict[str, str]):
        self.info_grid.clear_widgets()
        label_w = dp(140)

        def add_row(lbl: str, val: str):
            key = Label(text=f"[b]{lbl}:[/b]", markup=True, size_hint=(None, None),
                        width=label_w, halign="right", valign="top", color=(1,1,1,1))
            key.bind(size=lambda *_: setattr(key, "text_size", key.size))
            key.bind(texture_size=lambda *_: setattr(key, "height", key.texture_size[1]))

            v = Label(text=val or "—", size_hint=(1, None), halign="left", valign="top", color=(1,1,1,1))
            v.bind(size=lambda *_: setattr(v, "text_size", (v.width, None)))
            v.bind(texture_size=lambda *_: setattr(v, "height", max(v.texture_size[1], dp(20))))

            self.info_grid.add_widget(key)
            self.info_grid.add_widget(v)

        add_row("RUT",        data.get("numero_identificacion_fiscal", "—"))
        add_row("Dirección",  data.get("direccion_completa", "—"))
        add_row("Tipo de Pago", data.get("terminos_de_pago_del_cliente", "—"))
        add_row("Comuna",     data.get("comuna", "—"))
        add_row("Ciudad",     data.get("ciudad", "—"))
        add_row("Región",     data.get("estado", "—"))
        add_row("Vendedor",   data.get("vendedor", "—"))
        add_row("Email",      data.get("correo_electronico", "—"))

    # ---------- API: setear cliente ----------
    def set_client(self, selected: Dict[str, Any]):
        self._selected = selected or {}
        self._full = _fetch_full_client(self._selected)

        # rowid/estado para la lógica de precios
        self._cliente_rowid = self._selected.get("cliente_id")  # viene de tomar_pedido
        self._cliente_estado = self._full.get("estado") or self._selected.get("estado")

        display = self._selected.get("display") \
            or self._full.get("nombre_completo") or self._full.get("nombre_fantasia") or "—"
        self.title.text = f"Resumen de cliente:\n{display}"

        self._render_info(self._full)

        # Mostrar/ocultar botón Retomar según exista borrador
        has_draft = draft_exists(self._current_user, int(self._cliente_rowid or 0))
        self._retomar_btn.disabled = not has_draft
        self._retomar_btn.opacity = 1 if has_draft else 0
        self._retomar_btn.unbind(on_release=self._go_retomar)
        if has_draft:
            self._retomar_btn.bind(on_release=self._go_retomar)

        # reset de selección (por si cambias de cliente)
        self.shipping_spinner.text = "Seleccione…"
        self.region_spinner.text = "Seleccione región…"
        self.shipping_mode = None
        self.price_region = None
        self.next_btn.disabled = True

    # ---------- Navegación ----------
    def _back(self, *_):
        if self.manager:
            self.manager.transition = NoTransition()
            self.manager.current = "tomar_pedido"

    def _continue(self, *_):
        # Validación mínima (excepto cuando venimos de retomar y carrito cargará el contexto)
        app = App.get_running_app()
        coming_from_draft = bool(getattr(app, "order_ctx", {}).get("from_draft"))
        if not coming_from_draft:
            if self.shipping_mode is None:
                return
            if self.shipping_mode == "despacho" and (self._cliente_estado in (None,"","—","-","NULL","None")) \
               and not self.price_region:
                return

            app.order_ctx = {
                "mode": self.shipping_mode,                 # "retiro" | "despacho"
                "region": self.price_region,                # ej. "Metropolitana (CL)"
                "cliente_rowid": self._cliente_rowid,
                "cliente_display": self.title.text.replace("Resumen de cliente:\n", ""),
                "from_draft": False,
                # además de lo que ya pones:
                "cliente_rut": self._full.get("numero_identificacion_fiscal"),
                "cliente_direccion": self._full.get("direccion_completa"),
                "cliente_comuna": self._full.get("comuna"),
                "cliente_ciudad": self._full.get("ciudad"),
                "cliente_estado": self._full.get("estado"),
                "cliente_email": self._full.get("correo_electronico"),
                "forma_pago": self._full.get("terminos_de_pago_del_cliente"),
                # si no tienes dirección de despacho específica, por ahora replicamos dirección:
                "direccion_despacho": self._full.get("direccion_completa"),

            }

        # Ir a carrito
        if self.manager:
            self.manager.transition = NoTransition()
            self.manager.current = "carrito"
