import os


def get_bool_env(var_name, default: bool) -> bool:
    str_value = os.getenv(var_name, str(default)).lower()
    if str_value in ("true", "1", "yes"):
        return True
    elif str_value in ("false", "0", "no"):
        return False
    raise RuntimeError(f"Invalid boolean value for env {var_name}={str_value}")
