import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def merge_nested_dicts(dict1: dict, dict2: dict):
    merged_dict = defaultdict(dict)

    merged_dict.update(dict1)
    for key, nested_dict in dict2.items():
        if merged_dict.get(key) is None:
            merged_dict[key].update(nested_dict)
        else:
            for nested_key, value in nested_dict.items():
                new = merged_dict.get(key).get(nested_key, 0)
                old = nested_dict.get(nested_key, 0)
                diff = abs(new - old)
                if diff > 0:
                    merged_dict[key][nested_key] = old + diff

    return merged_dict
