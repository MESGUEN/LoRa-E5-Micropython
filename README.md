# LoRaE5 MicroPython Driver (UART / AT Commands)

A lightweight MicroPython class to control a **Seeed LoRa-E5** (or compatible AT-command LoRaWAN module) over **UART**.  
It focuses on the essentials needed in IoT projects:

- Send generic AT commands for configuration (`send_at`)
- Perform LoRaWAN join (`join_ok`)
- Send an uplink with hex payload and optionally receive a downlink (`send_payload_hex`)

This module is designed to integrate nicely with an **application state machine** (INIT / CONFIG / JOIN / MEASURE / TX).

---

## Features

- **Simple API** (small number of methods)
- **Non-blocking style loops with timeouts** (no long `sleep(600)`)
- Handles typical LoRa-E5 responses including:
  - `"joined"` / `"already joined"`
  - `"failed"`
  - `"Please join network first"` (NOT_JOINED)
  - `"RX "...""` downlink extraction (hex)
  - `"Done"`
- Return codes are **explicit strings** (easy to use in a state machine)

---

## Requirements

- MicroPython (ESP32 / ESP32-C3 / etc.)
- A UART object created with `machine.UART`
- LoRa-E5 wired correctly (TX/RX crossed, common GND)

> Note: On MicroPython, file and import names are case-sensitive.  
> If your file is named `LoraE5.py`, import it as `from LoraE5 import LoRaE5`.

---

## Installation

Copy `LoraE5.py` to your board filesystem, for example:

- `/LoraE5.py`
- or `/lib/LoraE5.py`

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

### `send_payload_hex(hex_payload, timeout_ms=8000) -> str`
Sends `AT+MSGHEX="..."` and returns:
- `"NOT_JOINED"` if the module is not joined (ex: `Please join network first`)
- `"<DOWNLINK_HEX>"` if a downlink was received (returns the hex string between quotes after `RX`)
- `"DONE"` if the send sequence completed without downlink
- `"TIMEOUT"` if **no UART data** arrived before timeout

---

## Quick Start

```python
from machine import UART
from LoraE5 import LoRaE5

uart = UART(1, baudrate=9600, tx=5, rx=4)   # adapt pins/UART id to your board
e5 = LoRaE5(uart)

# Ping the module
print(e5.send_at("AT"))   # 1 if response received, else 0
