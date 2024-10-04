import can

bus = can.Bus('ws://localhost:54701/',
                      interface='remote',
                      bitrate=500000,
                      receive_own_messages=True)
bus.set_filters([{"can_id": 0x12F, "can_mask": 0xFFF, "extended": False}])

def on_message_received(msg):
    print(msg)

notifier = can.Notifier(bus, [on_message_received])

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopped by user")
    notifier.stop()