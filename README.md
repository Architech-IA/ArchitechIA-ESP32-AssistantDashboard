# Orión ESP32 Dashboard

Dashboard de métricas ArchiTechIA para ESP32-S3 + OLED SH1106 128x64.

## Hardware

- ESP32-S3
- OLED 1.3" 128x64 (controlador SH1106, I2C)
  - SDA → GPIO 8
  - SCL → GPIO 9

## Setup

1. Instalar MicroPython v1.28+ en el ESP32
2. Editar `config.py` con tu WiFi y URL del portal
3. Subir los 3 archivos con `upload.py` (desde el directorio raíz del repo)

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Loop principal: WiFi, fetch de métricas, rotación de pantallas |
| `sh1106.py` | Driver OLED SH1106 en MicroPython |
| `config.py` | Configuración (WiFi, API URL, pines, intervalos) |

## Pantallas

Rota cada 4 segundos entre:
- Sprint activo (barra de progreso)
- Backlog (pendiente / en curso / completado)
- Épicas activas
- Estado del sistema (timestamp)

## WebREPL (actualización OTA)

El WebREPL arranca automáticamente después de conectar WiFi (puerto 8266, password `orion123`).
Para subir archivos por WiFi usar `webrepl_cli.py` de MicroPython.
