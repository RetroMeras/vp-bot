class BusConfig:
    MAX_STOP_NAME_LENGTH = 25
    MIN_STOP_NAME_LENGTH = 3
    STOP_CODE_LENGTH = 5

class CSVColumns:
    BUS_STOP = ['stop_code', 'name'] + ['latitude', 'longitude', 'is_active']
    BUS_ROUTE = ['route_number', 'name', 'first_stop_code', 'last_stop_code', 'is_active', 'color_hex']