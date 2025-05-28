from machine import UART
import time

uart = UART(0, baudrate=9600, tx=0, rx=1)


# 割り込みハンドラ
def receive_data(u):
    if u.any():
        data = u.read()
        if data and b"\x02" in data and b"\x03" in data:
            frame = data[1:-1]  # STXとETXを除いた中身
            try:
                print("Recv>", frame.decode())
            except UnicodeDecodeError:
                print("Recv> (decode error):", frame)


# UART割り込み
uart.irq(handler=receive_data, trigger=UART.IRQ_RXIDLE)


# そのまま送信
def send_data(data):
    if isinstance(data, str):
        data = data.encode()
    uart.write(data)


# STX,ETXを追加して送信
def send_command_frame(data):
    if isinstance(data, str):
        framed = b"\x02" + data.encode() + b"\x03"
        uart.write(framed)


print("Waiting for AKU-67 startup...")
time.sleep(1)

try:
    while True:
        user_input = input("Send> ")
        if user_input == "***":
            send_data("***")
        else:
            send_command_frame(user_input)
        time.sleep(0.2)

except KeyboardInterrupt:
    send_command_frame("Q")
    print("Exiting interactive mode.")
