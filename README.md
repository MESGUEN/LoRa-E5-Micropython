# LoRaE5 MicroPython Driver (UART / AT Commands)

A lightweight MicroPython class to control a **Seeed LoRa-E5** (or compatible AT-command LoRaWAN module) over **UART**.  
It focuses on the essentials needed in IoT projects:

- Send generic AT commands for configuration (`send_at`)
- Perform LoRaWAN join (`join_ok`)
- Send an uplink with hex payload and optionally receive a downlink (`send_payload_hex`)


## Requirements

- MicroPython (ESP32 / ESP32-C3 / etc.)
- A UART object created with `machine.UART`
- LoRa-E5 wired correctly (TX/RX crossed, common GND)


## Installation

Copy `LoRaE5.py` to your board filesystem, for example:

- `/LoRaE5.py`
- or `/lib/LoRaE5.py`

Then import it in your script.

---

## Public API

### `LoRaE5(uart)`
Constructor. Pass a configured `machine.UART` instance.

### `send_at(cmd, timeout_ms=2000) -> int`
Send a generic AT command (useful for configuration).  
Returns:
- `1` if **any character** was received before timeout
- `0` otherwise

### `join_ok(timeout_ms=15000) -> str`
Sends `AT+JOIN` and returns:
- `"JOIN"` if join succeeded (`joined` or `already joined`)
- `"FAILED"` if the word `failed` appears
- `"TIMEOUT"` otherwise

### `send_payload_hex(hex_payload, timeout_ms=10000) -> str`
Sends `AT+MSGHEX="..."` and returns:
- `"NOT_JOINED"` if the module is not joined (ex: `Please join network first`)
- `"<DOWNLINK_HEX>"` if a downlink was received (returns the hex string between quotes after `RX`)
- `"DONE"` if the send sequence completed without downlink
- `"TIMEOUT"` if **no UART data** arrived before timeout

---

## Quick Start

```python
from time import sleep
from machine import UART
from LoRaE5 import LoRaE5

uart = UART(1, baudrate=9600, tx=5, rx=4)
sleep(1)    # 1s delay to let the LoRa-E5 module boot
e5 = LoRaE5(uart)

# --- LoRaWAN configuration
e5.send_at("AT+RESET")
e5.send_at("AT+MODE=LWOTAA")
e5.send_at("AT+DR=EU868")
e5.send_at("AT+CH=NUM,0-2")
e5.send_at('AT+KEY=APPKEY,"YOUR_APPKEY_HERE"')
e5.send_at("AT+CLASS=A")
e5.send_at("AT+PORT=8")
e5.send_at("AT+LW=JDC,OFF")

# --- Join loop ---
while True:
    status = e5.join_ok()
    if status == "JOIN":
        break
    print("Waiting 30s before retry")
    sleep(30)

# --- Send a test payload (hex) ---
print("TX:", e5.send_payload_hex("01020304"))

