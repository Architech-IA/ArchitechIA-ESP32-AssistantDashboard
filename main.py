import network
import urequests
import ujson
import time
from machine import SoftI2C, Pin, reset
from sh1106 import SH1106
import config

OTA_VERSION_URL = "https://raw.githubusercontent.com/Architech-IA/ArchitechIA-ESP32-AssistantDashboard/main/version.txt"
OTA_BASE_URL    = "https://raw.githubusercontent.com/Architech-IA/ArchitechIA-ESP32-AssistantDashboard/main/"
OTA_FILES       = ["main.py", "sh1106.py"]

def center(text, width=16):
    return text[:width].center(width)

def trunc(text, n=16):
    return text[:n]

def draw_header(oled, title):
    oled.fill(0)
    oled.text(center(title), 0, 0)
    oled.hline(0, 10, 124)

def show_connecting(oled):
    oled.fill(0)
    oled.text("Conectando WiFi", 0, 24)
    oled.text("  ArchiTechIA  ", 0, 40)
    oled.show()

def show_error(oled, msg):
    oled.fill(0)
    oled.text("! ERROR !", 28, 0)
    oled.hline(0, 10, 128)
    oled.text(trunc(msg, 16), 0, 20)
    oled.text(trunc(msg[16:], 16), 0, 32)
    oled.show()

def show_ota(oled, msg):
    oled.fill(0)
    oled.text("OTA Update", 24, 0)
    oled.hline(0, 10, 124)
    oled.text(msg, 0, 28)
    oled.show()

def page_sprint(oled, sprint):
    draw_header(oled, "SPRINT ACTIVO")
    name = trunc(sprint.get("code", sprint.get("name", "?")), 16)
    oled.text(name, 0, 14)
    done  = sprint.get("done", 0)
    total = sprint.get("total", 0)
    oled.text("Tasks: " + str(done) + "/" + str(total), 0, 26)
    bar_w = 118
    oled.rect(5, 38, bar_w, 8)
    if total > 0:
        filled = int(bar_w * done / total)
        if filled > 0:
            for x in range(5, 5 + filled):
                oled.fb.vline(x, 38, 8, 1)
    pct = int(done * 100 / total) if total > 0 else 0
    oled.text(str(pct) + "% completado", 0, 52)
    oled.show()

def page_backlog(oled, backlog):
    draw_header(oled, "BACKLOG")
    todo = backlog.get("todo", 0)
    wip  = backlog.get("in_progress", 0)
    done = backlog.get("done", 0)
    tot  = backlog.get("total", todo + wip + done)
    oled.text("Pendiente:  " + str(todo), 0, 16)
    oled.text("En curso:   " + str(wip), 0, 28)
    oled.text("Completado: " + str(done), 0, 40)
    oled.hline(0, 52, 124)
    oled.text("Total:      " + str(tot), 0, 54)
    oled.show()

def page_epics(oled, epics):
    draw_header(oled, "EPICAS")
    active = epics.get("active", 0)
    oled.text(str(active), 52, 28)
    oled.text("activas", 40, 42)
    oled.show()

def page_status(oled, ts, version):
    draw_header(oled, "ORION v" + version)
    t = ts[11:16] if len(ts) >= 16 else "--:--"
    d = ts[:10]   if len(ts) >= 10 else "----"
    oled.text("Update: " + t, 0, 16)
    oled.text(d, 24, 28)
    oled.text("architechia.co", 0, 50)
    oled.show()

def connect_wifi(oled):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        show_connecting(oled)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
    if not wlan.isconnected():
        show_error(oled, "Sin WiFi")
        return False
    try:
        import webrepl
        webrepl.start(password='orion123')
    except Exception:
        pass
    return True

def fetch_metrics():
    try:
        r = urequests.get(config.API_URL, timeout=10)
        if r.status_code == 200:
            data = ujson.loads(r.text)
            r.close()
            return data
        r.close()
    except Exception as e:
        print("fetch error:", e)
    return None

def get_local_version():
    try:
        with open("version.txt") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"

def check_ota(oled):
    try:
        r = urequests.get(OTA_VERSION_URL, timeout=10)
        remote = r.text.strip()
        r.close()
        if remote == get_local_version():
            return
        show_ota(oled, "v" + remote + " disponible")
        time.sleep(1)
        for fname in OTA_FILES:
            show_ota(oled, "Bajando " + fname)
            r = urequests.get(OTA_BASE_URL + fname, timeout=20)
            with open(fname + ".tmp", "w") as f:
                f.write(r.text)
            r.close()
        import os
        for fname in OTA_FILES:
            try:
                os.remove(fname)
            except Exception:
                pass
            os.rename(fname + ".tmp", fname)
        with open("version.txt", "w") as f:
            f.write(remote)
        show_ota(oled, "Reiniciando...")
        time.sleep(2)
        reset()
    except Exception as e:
        print("OTA error:", e)

def run():
    i2c  = SoftI2C(scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA), freq=400000)
    oled = SH1106(i2c, addr=config.OLED_ADDR)

    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        if not connect_wifi(oled):
            return

    version    = get_local_version()
    data       = None
    last_fetch = 0
    last_ota   = 0
    page_idx   = 0
    last_page  = 0

    while True:
        now = time.time()

        if (now - last_ota) >= config.OTA_INTERVAL:
            check_ota(oled)
            last_ota = now

        if data is None or (now - last_fetch) >= config.POLL_INTERVAL:
            new_data = fetch_metrics()
            if new_data:
                data = new_data
            last_fetch = now

        if data and (now - last_page) >= config.PAGE_DURATION:
            sprints = data.get("sprints", [])
            backlog = data.get("backlog", {})
            epics   = data.get("epics",   {})
            ts      = data.get("ts",      "")

            pages = []
            for s in sprints:
                pages.append(("sprint", s))
            pages.append(("backlog", backlog))
            if epics.get("active", 0) > 0:
                pages.append(("epics", epics))
            pages.append(("status", ts))

            if pages:
                kind, payload = pages[page_idx % len(pages)]
                if kind == "sprint":
                    page_sprint(oled, payload)
                elif kind == "backlog":
                    page_backlog(oled, payload)
                elif kind == "epics":
                    page_epics(oled, payload)
                elif kind == "status":
                    page_status(oled, payload, version)
                page_idx += 1

            last_page = now
        elif data is None:
            show_error(oled, "Esperando datos")

        time.sleep(1)

run()
