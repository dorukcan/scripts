import asyncio
import concurrent.futures
import csv
import datetime
import json
import multiprocessing
import platform
from pprint import pprint

import requests


def main():
    tt = TT()

    result = []

    for i in range(1, 30 + 1):
        sync_run(i)
        diff = tt.log(f"sync {i}")
        result.append({"mode": "sync", "size": i, "diff": diff.total_seconds()})

        asyncio_run(i)
        diff = tt.log(f"asyncio {i}")
        result.append({"mode": "asyncio", "size": i, "diff": diff.total_seconds()})

        threading_run(i)
        diff = tt.log(f"threading {i}")
        result.append({"mode": "threading", "size": i, "diff": diff.total_seconds()})

        multiprocessing_run(i)
        diff = tt.log(f"multiprocessing {i}")
        result.append({"mode": "multiprocessing", "size": i, "diff": diff.total_seconds()})

    pprint(result)
    to_csv(result, 'async_test_result')


def test():
    tt = TT()

    result = []

    for i in range(1, 50):
        threading_run(200, i)
        diff = tt.log(i)
        result.append({'max_workers': i, 'diff': diff.total_seconds()})

    to_csv(result, 'threading')


def work(idx):
    url = f"https://jsonplaceholder.typicode.com/todos/{idx}"
    response = requests.get(url).text
    content = json.loads(response)
    return content['id']


################################################


def threading_run(max_idx, max_workers=8):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(work, list(range(1, max_idx + 1)))

    response = list(futures)


################################################


def multiprocessing_run(max_idx):
    with multiprocessing.Pool() as pool:
        futures = pool.map(work, list(range(1, max_idx + 1)))

    response = list(futures)


################################################


def asyncio_run(max_idx):
    loop = asyncio.get_event_loop()

    futures = []

    for i in range(1, max_idx + 1):
        futures.append(asyncio_work(i))

    response = loop.run_until_complete(asyncio.gather(*futures))


async def asyncio_work(idx):
    return work(idx)


################################################


def sync_run(max_idx):
    response = []

    for i in range(1, max_idx + 1):
        response.append(work(i))


################################################


def to_csv(dict_list, file_name):
    field_names = list(dict_list[0].keys())

    with open(file_name + '.csv', 'w', encoding="utf-8") as output_file:
        kwargs = {}

        # Deal with Windows inserting an extra '\r' in line terminators
        if platform.system() == 'Windows':
            kwargs = {'lineterminator': '\n'}

        dict_writer = csv.DictWriter(
            f=output_file,
            fieldnames=field_names,
            quoting=csv.QUOTE_NONNUMERIC,
            **kwargs
        )

        dict_writer.writeheader()
        dict_writer.writerows(dict_list)


class TT:
    def __init__(self):
        self.last_dt = datetime.datetime.now()

    def log(self, message=None):
        current_dt = datetime.datetime.now()
        diff = current_dt - self.last_dt

        print(current_dt, '#', 'elapsed:', diff, '#', message)
        self.last_dt = current_dt

        return diff


if __name__ == '__main__':
    main()
