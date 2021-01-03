import concurrent.futures
import hashlib
import os
import queue
from collections import defaultdict


class DuplicateFileFinder:
    """
    Finds duplicate files recursively.
    """

    def __init__(self):
        """
        Initialize buckets.
        """

        self.unseen = queue.Queue()
        self.file_list = queue.Queue()
        self.hash_table = defaultdict(set)

        self.max_worker = 8

    def run(self, starting_point):
        """
        Starts crawling process with an initial path.

        Put initial path to pool.

        Consume Paths
        Consume Hashes

        Detect Duplicates
        """
        self.unseen.put(starting_point)

        self.crawl(self.consume_paths)
        self.crawl(self.consume_hashes)

        return self.detect_duplicates()

    def crawl(self, worker):
        """
        asynchronous job runner
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_worker) as executor:
            futures = [executor.submit(worker) for _ in range(self.max_worker)]

            for future in concurrent.futures.as_completed(futures):
                future.result()

    def consume_paths(self):
        """
        consume unseen bucket to fill file_list bucket
        """
        while not self.unseen.empty():
            dir_path = self.unseen.get(block=False)

            for current_name in os.listdir(dir_path):
                current_path = os.path.join(dir_path, current_name)

                if os.path.isfile(current_path):
                    self.file_list.put(current_path)
                else:
                    self.unseen.put(current_path)

    def consume_hashes(self, buf_size=65536):
        """
        consume file_list bucket to fill hash_table
        """

        while not self.file_list.empty():
            file_path = self.file_list.get(block=False)
            sha1 = hashlib.sha1()

            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    sha1.update(data)

            hash_key = sha1.hexdigest()
            self.hash_table[hash_key].add(file_path)

    def detect_duplicates(self):
        """
        Detect algorithm
        """
        return [v for v in self.hash_table.values() if len(v) > 1]


if __name__ == '__main__':
    DuplicateFileFinder().run('/Users/doruk')
