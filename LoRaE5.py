import time
import re

class LoRaE5:
    def __init__(self, uart):
        self.uart = uart

    def send_at(self, cmd: str, timeout_ms: int = 2000) -> int:
        while self.uart.any():
            self.uart.read()

        self.uart.write(cmd + "\r\n")

        t0 = time.ticks_ms()
        got_any = False

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    got_any = True
            time.sleep_ms(10)

        return 1 if got_any else 0

    def join_ok(self, timeout_ms: int = 15000) -> str:
        while self.uart.any():
            self.uart.read()

        self.uart.write("AT+JOIN\r\n")

        t0 = time.ticks_ms()
        buf = bytearray()
        result = "TIMEOUT"  # valeur par défaut

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    buf.extend(data)
                    txt = bytes(buf).decode("ascii", "ignore").lower()

                    if "already joined" in txt or "joined" in txt:
                        result = "JOIN"
                        break
                    if "failed" in txt:
                        result = "FAILED"
                        break
            time.sleep_ms(10)

        return result

    def send_payload_hex(self, hex_payload: str, timeout_ms: int = 10000) -> str:
        while self.uart.any():
            self.uart.read()

        self.uart.write(f'AT+MSGHEX="{hex_payload}"\r\n')

        t0 = time.ticks_ms()
        buf = bytearray()
        saw_any = False

        rx_re = re.compile(r'RX[^"]*"([0-9A-Fa-f]+)"')

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    saw_any = True
                    buf.extend(data)
                    txt = bytes(buf).decode("ascii", "ignore")
                    low = txt.lower()

                    if "please join" in low:
                        return "NOT_JOINED"

                    m = rx_re.search(txt)
                    if m:
                        return m.group(1).upper()

                    if "done" in low:
                        return "DONE"

            time.sleep_ms(10)

        if not saw_any:
            return "TIMEOUT"
        return "DONE"
