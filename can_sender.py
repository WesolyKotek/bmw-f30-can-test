from time import sleep

import can

bus = can.Bus('ws://localhost:54701/',
                      interface='remote',
                      bitrate=500000,
                      receive_own_messages=True)

def send_message():
    # Send messages
    msgs = [can.Message(arbitration_id=0x12F, data=[2, 4, 3, 4, 5, 6, 7, 1]),
            can.Message(arbitration_id=0x130, data=[1, 2, 3, 4, 5, 6, 7, 8]),
            can.Message(arbitration_id=0x38, data=[1, 2, 3, 4, 5, 6, 7, 8])
            ]

    try:
        for msg in msgs:
            bus.send(msg)
            sleep(1)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        print("Message NOT sent")

try:
    while True:
        send_message()
except KeyboardInterrupt:
    print("Stopped by user")