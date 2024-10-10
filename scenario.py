import json
import time
import os


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

    def run(self):
        self.running = True
        repeats = self.scenario.get('repeats', 1)
        messages = self.scenario['messages']

        repeat_count = 0
        while self.running:
            repeat_count += 1
            print(f'{repeat_count}/inf' if repeats == -1 else f'{repeat_count}/{repeats}')

            self.send_uds_message(messages)

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
