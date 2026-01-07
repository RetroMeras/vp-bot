class BusConfig:
    MAX_STOP_NAME_LENGTH = 25
    MIN_STOP_NAME_LENGTH = 3
    STOP_CODE_LENGTH = 5
    BUS_STOP_COLUMNS = ['stop_code', 'name'] + ['latitude', 'longitude', 'is_active']
    BUS_ROUTE_COLUMNS = ['route_number', 'name', 'first_stop_code', 'last_stop_code', 'is_active', 'color_hex']