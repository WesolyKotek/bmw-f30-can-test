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
        stop_sequence = self.scenario['stop_check_message_responses']
        start_stop_check_message_interval = self.scenario.get('start_stop_check_message_interval', 1)
        start_stop_responses_timeout = self.scenario.get('start_stop_responses_timeout', 1)

        while self.running:
            if start_check_message and start_sequence:
                print('Ищем стартовую последовательность...')
                start_sequence_found = await self.check_for_sequence(start_check_message,
                                                                     start_sequence,
                                                                     start_stop_responses_timeout,
                                                                     start_stop_check_message_interval)

                if start_sequence_found:
                    print('Стартовая последовательность найдена, выполняем сценарий.')
                else:
                    print('Прерывание')
            else:
                print('Стартовая последовательность не задана, переходим к выполнению сценария.')

            stop_sequence_task = None
            if stop_check_message and stop_sequence:
                stop_sequence_task = asyncio.create_task(
                    self.check_for_sequence(stop_check_message,
                                            stop_sequence,
                                            start_stop_responses_timeout,
                                            start_stop_check_message_interval)
                )

            repeat_count = 0
            while self.running:
                repeat_count += 1
                print(f'{repeat_count}/inf' if repeats == -1 else f'{repeat_count}/{repeats}')

                self.send_uds_message(messages)

                if stop_sequence_task and stop_sequence_task.done() and stop_sequence_task.result():
                    print('Конечная последовательность найдена, останавливаем сценарий.')
                    break

                if repeats != -1 and repeat_count >= repeats:
                    break

    def send_uds_message(self, messages):
        for message in messages:
            if not self.running:
                print('Scenario stopped')
                return
            data = message['data']
            delay = message['delay'] / 1000
            self.uds_client.send(data)
            time.sleep(delay)

    async def check_for_sequence(self, check_message, sequence, responses_timeout, check_message_interval):
        if not check_message:
            return True

        received_packets = []
        original_sequence = sequence.copy()
        sequence_copy = sequence.copy()

        first_correct_packet = False
        start_time = None

        while self.running:
            try:
                self.uds_client.send(check_message)

                packet = await self.uds_client.receive()

                if packet:
                    for response in packet:
                        if response == sequence_copy[0]:
                            received_packets.append(response)
                            sequence_copy.pop(0)
                            print(f'Найден правильный пакет: {response},'
                                  f'оставшиеся для получения: {len(sequence_copy)}')

                            if not first_correct_packet:
                                first_correct_packet = True
                                start_time = time.time()

                            if not sequence_copy:
                                print('Последовательность пакетов успешно найдена!')
                                return True
                        else:
                            print(f'Неправильный пакет, выкидываем и продолжаем искать.')

                if first_correct_packet and (time.time() - start_time > responses_timeout / 1000):
                    print('Таймер истек, сбрасываем буфер и начинаем поиск заново.')
                    received_packets.clear()
                    sequence_copy = original_sequence.copy()
                    first_correct_packet = False

            except asyncio.CancelledError:
                print('Поиск последовательности был остановлен.')
                break

            await asyncio.sleep(check_message_interval / 1000)

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
