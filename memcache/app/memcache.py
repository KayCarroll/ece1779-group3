import logging
import random
import time

logger = logging.getLogger(__name__)

# NOTE: Currently the assumption is that only the size of the values being stored in the cache 
# count towards the total cache memory capacity. The memory used by the keys and general python 
# code objects are not being counted towards the total memory usage.


class CacheItem:
    def __init__(self, key, value):
        """Initialize a cache item.

        Args:
            key (str): The key to associate with the given value.
            value (str): The base64 encoded value.
        """
        self.key = key
        self.size_in_mb = (len(value) * 3 / 4) / 1000000 # NOTE: This assumes value is a base64 encoded string
        self.time_last_used = time.time()
        self._value = value

    @property
    def value(self):
        """Get the value stored in the cache item.

        Note: Accessing this property will automatically update the time_last_used attribute of the cache item.
        """
        self.time_last_used = time.time()
        return self._value


class MemCache:
    def __init__(self, cache_id, capacity=0, replacement_policy=''):
        """Initialize memory cache.

        Args:
            cache_id (int): An integer indicating the id of this memcache instance.
            capacity (float): The capacity of the memory cache in MB.
            replacement_policy (str): The replacement policy to use when deciding what items in the cache to
                replace when needing to make space for adding a new item. Can have a value of either "RR" 
                (random replacement) or "LRU" (least recently used).
        """
        self.id = cache_id
        self.capacity = capacity
        self.replacement_policy = replacement_policy
        self.is_active = True
        self.cache = {}
        self.cache_misses = 0
        self.current_cache_size = 0
        self.requests_served = 0

    def _remove_item(self, key):
        """Remove a key-value pair from the cache.

        Args:
            key (str): The key of the value to be removed from the cache.
        """
        item_to_remove = self.cache.pop(key)
        self.current_cache_size -= item_to_remove.size_in_mb
        logger.debug(f'Removed item with key {key} and size {item_to_remove.size_in_mb}MB from cache.')

    def _remove_cache_items(self, target_cache_size):
        """Remove cached items until the current size of the cache is <= the given target cache size.

        Args:
            target_cache_size (float): The target size to reduce the cache to in MB.
        """
        logger.info(f'Removing items from cache. Current cache size: {self.current_cache_size} MB. '
                    f'Target cache size: {target_cache_size} MB')

        if self.replacement_policy == 'LRU':
            key_list = self.get_keys_ordered_by_lru()

        while self.current_cache_size > target_cache_size:
            if self.replacement_policy == 'LRU':
                key_to_remove = key_list.pop(0)
            else:
                key_to_remove = random.choice(list(self.cache))
            self._remove_item(key_to_remove)

        logger.debug(f'Cache size after removing item(s): {self.current_cache_size}')

    def activate(self):
        # TODO: Add logging and check if any additional logic needed to activate.
        self.is_active = True

    def deactivate(self):
        # TODO: Add logging and check if any additional logic needed to deactivate.
        self.is_active = False

    def get_keys_ordered_by_lru(self):
        """Get a list of keys currently in the cache ordered from least recently used to most recently used.

        Returns:
            list: The ordered list of keys.
        """
        return sorted(self.cache, key=lambda k: self.cache[k].time_last_used)

    def get_value(self, key):
        """Get the cached value associated with the given key.

        Args:
            key (str): The key of the value to be returned.

        Returns:
            str: The base64 encoded value associated with the given key.
        """
        if key in self.cache:
            value = self.cache[key].value
        else:
            self.cache_misses += 1
            value = None

        self.requests_served += 1
        return value

    def put_item(self, key, value):
        """Insert an item with the given key and value into the cache.

        Insert the key-value pair into the cache. If inserting the new value into the cache would cause the
        total memory capacity of the cache to be exceeded, then existing cached items will first be remove
        based on the configured replacement policy.

        Args:
            key (str): The key to associate with the given value.
            value (str): The base64 encoded value to be added to the cache.

        Raises:
            ValueError: A ValueError is raised if the size of the given value is greater than the total
                cache capacity and cannot be inserted into the cache.
        """
        new_item = CacheItem(key, value)

        if self.current_cache_size + new_item.size_in_mb > self.capacity:
            # Remove items from cache until enough space
            target_cache_size = self.capacity - new_item.size_in_mb
            if target_cache_size < 0:
                logger.error('Cannot insert an item that is larger than the configured cache capacity. '
                             f'Cache capacity: {self.capacity} MB. Item size: {new_item.size_in_mb} MB.')
                raise ValueError
            else:
                self._remove_cache_items(target_cache_size)

        self.cache[key] = new_item
        self.current_cache_size += new_item.size_in_mb

    def clear(self):
        """Clear the content of the cache.
        """
        self.cache.clear()
        self.current_cache_size = 0

    def invalidate_key(self, key):
        """Remove an item from the cache identified by the given key.

        Note: If the given key does not exist in the cache then a KeyError will be raised.

        Args:
            key (str): The key associated with the item to remove from the cache.
        """
        self._remove_item(key)

    def update_config(self, replacement_policy=None, capacity=None):
        """Update the configuration of the cache's replacement policy and/or total capacity.

        If the capacity of the cache is updated to be less than it's current capacity configuration,
        then items will be removed from the cache using the latest replacement policy that has been set.

        Args:
            replacement_policy (str, optional): The replacement policy to be used. If set,
                must have a value of either "RR" or "LRU". Defaults to None.
            capacity (float, optional): The total capacity of the cache in MB. Defaults to None.
        """
        if replacement_policy:
            self.replacement_policy = replacement_policy

        if capacity:
            self.capacity = capacity
            if self.current_cache_size > capacity:
                self._remove_cache_items(capacity)

        logger.info(f'Updated cache configuration. Cache now has capacity of {self.capacity} MB '
                    f'and a replacement policy of {self.replacement_policy}.')

    def get_statistics(self):
        """Get a dictionary containing statistics related to the cache's usage.

        Returns:
            dict: A dictionary containing the statistics being tracked by the memcache.
        """
        if self.requests_served:
            miss_rate = round(self.cache_misses / self.requests_served, 2)
            hit_rate = 1 - miss_rate
        else:
            miss_rate = 0
            hit_rate = 0

        return {'cache_id': self.id, 'is_active': int(self.is_active), 'cache_count': len(self.cache),
                'cache_size': self.current_cache_size, 'hit_rate': hit_rate, 'miss_rate': miss_rate,
                'requests_served': self.requests_served}
