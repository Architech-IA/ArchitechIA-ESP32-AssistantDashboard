# ── WiFi ──────────────────────────────────────────────────────────────
WIFI_SSID     = "URBANO_2.4G"
WIFI_PASSWORD = "Urbano123"

# ── API ───────────────────────────────────────────────────────────────
API_URL = "https://portal.architechia.co/api/metrics/display"

# ── Hardware ──────────────────────────────────────────────────────────
I2C_SDA  = 8
I2C_SCL  = 9
OLED_ADDR = 0x3C   # si no funciona, probá 0x3D

# ── Comportamiento ────────────────────────────────────────────────────
POLL_INTERVAL   = 60   # segundos entre llamadas a la API
PAGE_DURATION   = 4    # segundos por página en el OLED
