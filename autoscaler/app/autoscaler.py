from enum import Enum


class ScalingMode(Enum):
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'


class AutoScaler:
    def __init__(self, mode):
        self.mode = mode
        self.max_miss_rate = None
        self.min_miss_rate = None
        self.expand_pool_factor = None
        self.shrink_pool_factor = None

    def set_mode(self, mode):
        self.mode = mode

    def update_config(self, max_miss_rate=None, min_miss_rate=None, expand_ratio=None, shrink_ratio=None):
        if max_miss_rate:
            self.max_miss_rate = max_miss_rate
        if min_miss_rate:
            self.min_miss_rate = min_miss_rate
        if expand_ratio:
            self.expand_ratio = expand_ratio
        if shrink_ratio:
            self.shrink_ratio = shrink_ratio
