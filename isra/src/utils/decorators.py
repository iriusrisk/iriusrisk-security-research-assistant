import datetime

import time


def get_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        # print(f"Total execution time of {func}: {end_time - start_time} seconds")
        return result

    return wrapper


def audit(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.datetime.now()
            log_object = {
                "timestamp": str(start_time),
                "timestamp_unix": start_time.timestamp(),
                "message": message,
                "args": args
            }
            # TODO: Output to file
            # print(f"{log_object}")
            result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
