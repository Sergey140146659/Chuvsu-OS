import json
import random
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, filepath: str):
        with open(filepath, 'r') as f:
            config_data = json.load(f)

        self._system_specs = config_data.get("system_params", {})
        self._task_specs = config_data.get("task_params", {})

        self._system_config_cache: Dict[str, Any] = {}

    def _generate_value(self, spec: Dict[str, Any]) -> Any:

        min_val = spec["min"]
        max_val = spec["max"]
        step = spec["step"]

        if min_val == max_val:
            return min_val

        possible_values = []
        current_val = min_val
        while current_val <= max_val:
            possible_values.append(current_val)
            current_val += step

        if not possible_values:
            return min_val

        return random.choice(possible_values)

    def get_system_config(self) -> Dict[str, Any]:

        if self._system_config_cache is not None:
            return self._system_config_cache

        system_config = {}
        for name, spec in self._system_specs.items():
            system_config[name] = self._generate_value(spec)

        self._system_config_cache = system_config
        return self._system_config_cache

    def get_new_task_params(self) -> Dict[str, Any]:
        task_params = {}
        for name, spec in self._task_specs.items():
            task_params[name] = self._generate_value(spec)

        return task_params
