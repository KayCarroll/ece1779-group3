import logging
import random
import time

logger = logging.getLogger(__name__)

# TODO: Add in docstrings and logging in the classes below

# NOTE: Currently the assumption is that only the size of the values being stored in the cache 
# count towards the total cache memory capacity. The memory used by the keys and general python 
# code objects are not being counted towards the total memory usage.


class CacheItem:
    def __init__(self, key, value):
        self.key = key
        self.size_in_bytes = len(value) * 3 / 4 # NOTE: This assumes value is a base64 encoded string
        self.time_last_used = time.time()
        self._value = value

    @property
    def value(self):
        self.time_last_used = time.time()
        return self._value


class MemCache:
    def __init__(self, capacity=40, replacement_policy='RR'):
        # TODO: Either convert between MB and bytes where needed or keep everything in MB
        self.capacity = capacity
        self.replacement_policy = replacement_policy
        self.cache = {}
        self.cache_misses = 0
        self.current_cache_size = 0
        self.requests_served = 0

    def _remove_item(self, key):
        item_to_remove = self.cache.pop(key)
        self.current_cache_size -= item_to_remove.size_in_bytes

    def _remove_cache_items(self, target_cache_size):
        if self.replacement_policy == 'LRU':
            # TODO: Double check that the order is from least recently used to most recently used 
            # after the sorting. If in the wrong order, just remove the reverse=True
            key_list = sorted(self.cache, key=lambda k: self.cache[k].time_last_used, reverse=True)

        while self.current_cache_size > target_cache_size:
            if self.replacement_policy == 'LRU':
                key_to_remove = key_list.pop(0)
            else:
                key_to_remove = random.choice(list(self.cache))
            self._remove_item(key_to_remove)

    def get_value(self, key):
        if key in self.cache:
            value = self.cache[key].value
        else:
            self.cache_misses += 1
            value = None

        self.requests_served += 1
        return value

    def put_item(self, key, value):
        new_item = CacheItem(key, value)

        if self.current_cache_size + new_item.size_in_bytes > self.capacity:
            # Remove items from cache until enough space
            target_cache_size = self.capacity - new_item.size_in_bytes
            if target_cache_size < 0:
                # TODO: Consider raising an error
                # logger.error('Cannot insert an item that is larger than the configured cache capacity. '
                #              f'Cache capacity: {self.capacity} bytes. Item size: {new_item.size_in_bytes} bytes.')
                pass
            else:
                self._remove_cache_items(target_cache_size)

        self.cache[key] = new_item
        self.current_cache_size += new_item.size_in_bytes

    def clear(self):
        self.cache.clear()
        self.current_cache_size = 0

    def invalidate_key(self, key):
        self._remove_item(key)

    def update_config(self, replacement_policy=None, capacity=None):
        if replacement_policy:
            self.replacement_policy = replacement_policy

        if capacity:
            self.capacity = capacity
            if self.current_cache_size > capacity:
                self._remove_cache_items(capacity)

    def get_statistics(self):
        miss_rate = round(self.cache_misses / self.requests_served, 2)
        hit_rate = 1 - miss_rate
        return {'cache_count': len(self.cache), 'cache_size': self.current_cache_size,
                'hit_rate': hit_rate, 'miss_rate': miss_rate, 'requests_served': self.requests_served}
