import socket

import utils
from datetime import datetime


class UDSClient:
    def __init__(self, ip, tcp_port=6801):
        self.ip = ip
        self.tcp_port = tcp_port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.tcp_port))
        print(f'ENET connected to {self.ip}:{self.tcp_port} !')

    def close(self):
        if self.sock:
            self.sock.close()
            print('Connection closed!')

    def send(self, message: str):
        message_bytes = utils.str_to_b(message)
        self.sock.send(message_bytes)
        print(f'Send: {message}')

    def sendall(self, messages: list):
        messages_bytes = b''.join(utils.str_to_b(message) for message in messages)
        self.sock.sendall(messages_bytes)
        print(f'Send group: {"\n".join(messages)}')

    def receive(self):
        try:
            data = self.sock.recv(512)
            if not data:
                return []

            buffer = data
            messages = []

            while buffer:
                if len(buffer) < 6:
                    more_data = self.sock.recv(512)
                    if not more_data:
                        break
                    buffer += more_data

                payload_length = int.from_bytes(buffer[:4], byteorder='big')
                total_length = 4 + 2 + payload_length

                if len(buffer) < total_length:
                    more_data = self.sock.recv(512)
                    if not more_data:
                        break
                    buffer += more_data
                    continue

                message = buffer[:total_length]
                buffer = buffer[total_length:]

                message_str = ' '.join([f'{byte:02x}' for byte in message])
                datetime_current = datetime.now()
                print(f'Receive: {datetime_current.hour}:'
                      f'{datetime_current.minute}:'
                      f'{datetime_current.second}:'
                      f'{datetime_current.microsecond} '
                      f'{message_str}')
                messages.append(message)

            return messages

        except socket.timeout:
            print('RECEIVE TIMEOUT!')
            return []

    def send_and_receive(self, message: str):
        self.send(message)
        return self.receive()

    @staticmethod
    def scan_for_adapters(ip_range=['192.168.16.100'], udp_port=6811, timeout=2):
        adapter_info = []
        connection_message = utils.str_to_b('00 00 00 00 00 11')
        for ip in ip_range:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)

                sock.sendto(connection_message, (ip, udp_port))

                response, addr = sock.recvfrom(64)  # 6811 udp возвращает 56 байт

                if len(response) >= 17:
                    vin = response[-17:].decode('utf-8', errors='ignore')
                else:
                    continue

                adapter_info.append((addr[0], response))
                print(f'Find vehicle: {addr[0]}:{udp_port} - {vin}')

                sock.close()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error while scan {ip}:{udp_port} - {e}")
        return adapter_info
