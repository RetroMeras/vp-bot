class UserDataManager:
    """Centralizes user data storage operations"""

    def __init__(self):
        self._store = {}

    def set_stop_code(self, user_id: int, stop_code: str):
        if user_id not in self._store:
            self._store[user_id] = {}
        self._store[user_id]["stop_code"] = stop_code

    def set_name(self, user_id: int, stop_name: str):
        if user_id not in self._store:
            raise IndexError("First stop_code must be specified")
        self._store[user_id]["name"] = stop_name

    def set_location(self, user_id: int, latitude: float, longitude: float):
        if user_id not in self._store:
            raise IndexError("First stop_code must be specified")
        self._store[user_id]["latitude"] = latitude
        self._store[user_id]["longitude"] = longitude

    def get_stop_data(self, user_id: int, key: str | None = None):
        if key:
            return self._store.get(user_id, {}).get(key)
        return self._store.get(user_id, {})

    def clear_user_data(self, user_id: int):
        self._store.pop(user_id, None)

# Use as singleton
user_data_manager = UserDataManager()