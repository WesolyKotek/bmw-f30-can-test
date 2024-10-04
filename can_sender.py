import can

bus = can.Bus('ws://localhost:54701/',
                      interface='remote',
                      bitrate=500000,
                      receive_own_messages=True)

def send_message():
    # Send messages
    msg = can.Message(arbitration_id=0x12F, data=[1, 2, 3, 4, 5, 6, 7, 8])

    try:
        bus.send(msg)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        print("Message NOT sent")

try:
    while True:
        send_message()
except KeyboardInterrupt:
    print("Stopped by user")