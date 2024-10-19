import json
import time
import os

import asyncio


class Scenario:
    def __init__(self, filename, uds_client):
        self.filename = filename
        self.scenario = self.load_scenario()
        self.uds_client = uds_client
        self.messages_stop = []
        self.running = False

    def load_scenario(self):
        with open(self.filename, 'r') as file:
            return json.load(file)

    async def run(self):
        self.running = True
        repeats = self.scenario.get('repeats', 1)
        messages = self.scenario['messages']

        start_check_message = self.scenario['start_check_message']
        start_sequence = self.scenario['start_check_message_responses']
        stop_check_message = self.scenario['stop_check_message']
        stop_check_sequence = self.scenario['stop_check_message_responses']
        start_stop_responses_timeout = self.scenario.get('start_stop_responses_timeout', 1)

        if start_sequence:
            await self.check_for_sequence(start_check_message, start_sequence,
                                          stop_check_message, stop_check_sequence,
                                          start_stop_responses_timeout)

        repeat_count = 0
        while self.running:
            repeat_count += 1
            print(f'{repeat_count}/inf' if repeats == -1 else f'{repeat_count}/{repeats}')

            await self.send_uds_message(messages)

            if repeats != -1 and repeat_count >= repeats:
                break

    async def send_uds_message(self, messages):
        for message in messages:
            if not self.running:
                print('Scenario stopped')
                return
            data = message['data']
            delay = message['delay'] / 1000
            self.uds_client.send(data)
            time.sleep(delay)

    async def check_for_sequence(self,
                                 start_check_message, start_sequence,
                                 stop_check_message, stop_sequence,
                                 start_stop_responses_timeout):

        received_packets = []
        start_time = time.time()
        while not self.stop_event.is_set():
            try:
                packet = await asyncio.wait_for(self.uds_client.receive(),
                                                timeout=start_stop_responses_timeout)

                if packet:
                    print(f"Получен пакет: {packet}")

                    # Если пакет совпадает с ожидаемым элементом последовательности
                    if packet == sequence[0]:
                        received_packets.append(packet)
                        sequence.pop(0)
                        print(f"Найден правильный пакет, оставшиеся для получения: {len(sequence)}")

                        # Если вся последовательность найдена
                        if not sequence:
                            print("Последовательность пакетов успешно найдена!")
                            return True
                        else:
                            print(f"Неправильный пакет: {packet}, выкидываем и продолжаем искать.")
                    else:
                        print("Буфер пустой, ждем нового пакета.")

                except asyncio.TimeoutError:
                    print("Время ожидания пакета истекло.")
                    # Сбрасываем прогресс поиска последовательности и начинаем заново
                    received_packets.clear()
                    sequence = self.check_sequence.copy()

                    print("Последовательность не найдена.")
                    return False


    def stop(self):
        self.running = False

        time.sleep(0.5)

        messages_stop = self.scenario['messages_stop']
        if len(messages_stop) > 0:
            print('Stop messages:')
            self.send_uds_message(messages_stop)

        print('Scenario stopped')


def find_scenario_files(directory='scenarios'):
    scenario_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            scenario_files.append(os.path.join(directory, filename))
    return scenario_files


def scenarios_to_strs(files):
    scenarios = []
    for i, file in enumerate(files):
        with open(file, 'r') as f:
            scenario_data = json.load(f)
            scenario_name = scenario_data.get('name', 'Unknown')
            scenarios.append(f'{i}: {file} - {scenario_name}')
    return scenarios
