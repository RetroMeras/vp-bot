class BusConfig:
    MAX_STOP_NAME_LENGTH = 25
    MIN_STOP_NAME_LENGTH = 3
    STOP_CODE_LENGTH = 5
    CSV_REQUIRED_COLUMNS = ['stop_code', 'name']
    CSV_OPTIONAL_COLUMNS = ['latitude', 'longitude', 'is_active']