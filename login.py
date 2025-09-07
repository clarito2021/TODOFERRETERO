# --- Desactivar y limpiar caché del proyecto TODOFERRETERO (KISS) ---
import sys, os, shutil
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

_PROJECT_ROOT = Path(__file__).parent
for root, dirs, files in os.walk(_PROJECT_ROOT):
    if "__pycache__" in dirs:
        shutil.rmtree(Path(root) / "__pycache__", ignore_errors=True)
# --- fin caché ---

# -------------------- login.py --------------------
from typing import Optional
import sqlite3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import platform  # detectar Android/desktop

# --- Import dinámico de jnius SOLO en Android (evita warnings en desktop) ---
_autoclass: Optional[object] = None
if platform == "android":
    try:
        from jnius import autoclass as _autoclass  # type: ignore[import-not-found]
    except Exception:
        _autoclass = None

# pantallas del proyecto
from tomar_pedido import TakeOrderScreen
from resumen_cliente import ClientSummaryScreen
from carrito import CartScreen
from historial import HistoryScreen

# Seguridad opcional
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False

# Rutas
DB_PATH = Path("bd_sqlite/todoferre.db").expanduser().resolve()
LOGO_PATH = Path("images/logo-cuadrado-ferretero.png")

def fetch_password_hash(username: str) -> Optional[str]:
    if not DB_PATH.exists():
        return None
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT password_hash FROM usuarios WHERE username_ferro = ?",
            (username.strip(),),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        con.close()

def check_password(plaintext: str, stored: Optional[str]) -> bool:
    if stored is None:
        return False
    if stored.startswith("$2") and HAS_BCRYPT:
        try:
            return bcrypt.checkpw(plaintext.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            return False
    return plaintext == stored

# ---------- Campo redondeado ----------
class RoundedInput(FloatLayout):
    def __init__(self, hint_text: str = "", password: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(56)
        with self.canvas.before:
            Color(0.20, 0.20, 0.20, 1)
            self.bg = RoundedRectangle(radius=[12], pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.input = TextInput(
            hint_text=hint_text,
            multiline=False,
            password=password,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(1, 1, 1, 0.6),
            cursor_color=(1, 1, 1, 1),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.add_widget(self.input)

    def _update_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

    @property
    def text(self) -> str:
        return self.input.text

    def focus(self):
        self.input.focus = True

# ---------- Botón redondeado ----------
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(56)
        with self.canvas.before:
            Color(0.85, 0.12, 0.12, 1)
            self.rect = RoundedRectangle(radius=[20], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

# ---------- Pantalla de Login ----------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Solo fijamos tamaño de ventana en ESCRITORIO. En Android se ignora.
        if platform in ("linux", "win", "macosx"):
            Window.size = (420, 640)

        root = BoxLayout(orientation="vertical", padding=24, spacing=16)

        if LOGO_PATH.exists():
            logo = Image(
                source=str(LOGO_PATH),
                size_hint=(1, 0.35),
                allow_stretch=True,
                keep_ratio=True,
            )
            subtitle = Label(text="Login Ventas", font_size=20, size_hint=(1, 0.10))
            root.add_widget(logo)
            root.add_widget(subtitle)
        else:
            title = Label(text="TODOFERRE - Login", font_size=22, size_hint=(1, 0.20))
            root.add_widget(title)

        self.user_field = RoundedInput(hint_text="Usuario", size_hint=(1, None))
        self.pass_field = RoundedInput(
            hint_text="Contraseña", password=True, size_hint=(1, None)
        )
        self.msg = Label(text="", color=(1, 0.2, 0.2, 1), size_hint=(1, 0.10))

        login_btn = RoundedButton(text="Ingresar", size_hint=(1, None))
        login_btn.bind(on_release=self._on_login)

        root.add_widget(self.user_field)
        root.add_widget(self.pass_field)
        root.add_widget(self.msg)
        root.add_widget(login_btn)
        self.add_widget(root)

        self.user_field.focus()

    def _on_login(self, *_):
        username = self.user_field.text.strip()
        password = self.pass_field.text

        if not username or not password:
            self.msg.text = "Ingrese usuario y contraseña."
            return

        stored = fetch_password_hash(username)
        if check_password(password, stored):
            # guardar usuario para borradores/órdenes
            App.get_running_app().current_user = username
            # pasar a tomar pedido
            self.manager.transition = NoTransition()
            take = self.manager.get_screen("tomar_pedido")   # nombre canónico
            if hasattr(take, "set_user"):
                take.set_user(username)
            self.manager.current = "tomar_pedido"
        else:
            self.msg.text = "Credenciales inválidas."

# ---------- App ----------
class RootApp(App):
    title = "TODO FERRETERO"
    current_user: Optional[str] = None

    def build(self):
        print("[RootApp] build() – plataforma:", platform)
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(TakeOrderScreen(name="tomar_pedido"))
        sm.add_widget(ClientSummaryScreen(name="resumen_cliente"))
        sm.add_widget(CartScreen(name="carrito"))
        sm.add_widget(HistoryScreen(name="historial"))
        return sm

    def on_start(self):
        # En Android, fija orientación retrato en el Activity
        if platform == "android" and _autoclass:
            PythonActivity = _autoclass('org.kivy.android.PythonActivity')
            ActivityInfo = _autoclass('android.content.pm.ActivityInfo')
            PythonActivity.mActivity.setRequestedOrientation(
                ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                # Si quisieras permitir retrato “invertido”:
                # ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT
            )

if __name__ == "__main__":
    print("Usando DB:", DB_PATH)
    print("Logo existe:", LOGO_PATH.exists(), "-", LOGO_PATH.resolve())
    RootApp().run()
