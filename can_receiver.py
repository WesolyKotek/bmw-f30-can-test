import can

filters = [{"can_id": 0x12F, "can_mask": 0xFFF}]
bus = can.Bus('ws://localhost:54701/',
                      interface='remote',
                      bitrate=500000,
                      receive_own_messages=True,
                      can_filters=filters)
logger = can.Printer(file="log.txt", append=True)

def on_message_received(msg):
    print(msg)

notifier = can.Notifier(bus, [on_message_received, logger])

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopped by user")
    notifier.stop()