import time
import re

class LoRaE5:
    def __init__(self, uart):
        self.uart = uart

    def send_at(self, cmd: str, timeout_ms: int = 2000) -> int:
        while self.uart.any():
            self.uart.read()
        print(cmd)
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

        print("Tentative JOIN")
        self.uart.write("AT+JOIN\r\n")

        t0 = time.ticks_ms()
        buf = bytearray()
        
        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    buf.extend(data)
                    txt = bytes(buf).decode("latin-1")
                    if "joined" in txt:
                        print("JOINED")
                        return "JOINED"
                
                    if "failed" in txt:
                        print("FAILED")
                        return "FAILED"
            time.sleep_ms(10)

        return "TIMEOUT"

    def send_payload_hex(self, hex_payload: str, timeout_ms: int = 10000) -> str:
        while self.uart.any():
            self.uart.read()

        print("Emission: ", hex_payload)
        self.uart.write(f'AT+MSGHEX="{hex_payload}"\r\n')

        t0 = time.ticks_ms()
        buf = bytearray()

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    buf.extend(data)
                    txt = bytes(buf).decode("latin-1")
                    if "Please join" in txt:
                        return "NOT_JOINED"

                    idx = txt.find('RX: "')	# recherche d'un downlink
                    if idx != -1:
                        start = idx + 5
                        end = txt.find('"', start)
                        if end != -1:
                            return txt[start:end].strip()

                    if "Done" in txt:
                        return "DONE"

            time.sleep_ms(10)

        return "TIMEOUT"

        
