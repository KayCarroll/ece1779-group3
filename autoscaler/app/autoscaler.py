import logging

from enum import Enum

logger = logging.getLogger(__name__)


class ScalingMode(Enum):
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'


class AutoScaler:
    def __init__(self, mode, max_miss_rate=0.8, min_miss_rate=0.2, expand_ratio=2, shrink_ratio=0.5):
        self.mode = mode
        self.max_miss_rate = max_miss_rate
        self.min_miss_rate = min_miss_rate
        self.expand_ratio = expand_ratio
        self.shrink_ratio = shrink_ratio

    def set_mode(self, mode):
        self.mode = mode

    def update_config(self, max_miss_rate=None, min_miss_rate=None, expand_ratio=None, shrink_ratio=None):
        if max_miss_rate:
            self.max_miss_rate = float(max_miss_rate)
        if min_miss_rate:
            self.min_miss_rate = float(min_miss_rate)
        if expand_ratio:
            self.expand_ratio = float(expand_ratio)
        if shrink_ratio:
            self.shrink_ratio = 1/float(shrink_ratio)

    def get_target_node_count(self, miss_rates, active_node_count):
        if not miss_rates:
            logger.error(f'Cannot execute auto scaling. No miss rate metrics available.')
            return active_node_count

        average_miss_rate = sum(miss_rates)/len(miss_rates)

        if average_miss_rate > self.max_miss_rate:
            target_node_count = int(active_node_count * self.expand_ratio)
        elif average_miss_rate < self.min_miss_rate:
            target_node_count = int(active_node_count * self.shrink_ratio)
        else:
            target_node_count = active_node_count

        return target_node_count
