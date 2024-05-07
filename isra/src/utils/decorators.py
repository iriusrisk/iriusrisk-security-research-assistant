import time


def get_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        # print(f"Total execution time of {func}: {end_time - start_time} seconds")
        return result

    return wrapper
