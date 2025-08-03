# priority_queue.py
import heapq

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, score, url):
        heapq.heappush(self.queue, (-score, url))  # max-heap

    def pop(self):
        if self.queue:
            return heapq.heappop(self.queue)[1]
        return None

    def is_empty(self):
        return len(self.queue) == 0