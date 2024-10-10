from uds import UDSClient
import scenario

if __name__ == "__main__":
    adapters = UDSClient.scan_for_adapters()

    if not adapters:
        print('No one vehicle find')
        exit()

    adapter_ip = adapters[0][0]

    uds_client = UDSClient(ip=adapter_ip)
    uds_client.connect()

    scenario_files = scenario.find_scenario_files()

    if not scenario_files:
        print('Scenarios not found')
        exit()

    scenarios = '\n'.join(scenario.scenarios_to_strs(scenario_files))
    print(f'Scenarios:\n{scenarios}')

    try:
        while True:
            selected_index = int(input())

            if 0 <= selected_index < len(scenario_files):
                scenario_file = scenario_files[selected_index]
                print(f'Run scenario: {scenario_file}')
                _scenario = scenario.Scenario(scenario_file, uds_client)

                try:
                    _scenario.run()
                except KeyboardInterrupt:
                    _scenario.stop()
            else:
                print('Wrong input')
    except KeyboardInterrupt:
        pass

    uds_client.close()