def binary_search(sorted_items, get_key, target):
    # time: O(log n), extra space: O(1)
    low = 0
    high = len(sorted_items) - 1
    while low <= high:
        middle = (low + high) // 2
        value = get_key(sorted_items[middle])
        if value == target:
            return middle
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def first_index_at_least(sorted_items, get_key, minimum):
    # time: O(log n), extra space: O(1)
    low = 0
    high = len(sorted_items) - 1
    result = -1
    while low <= high:
        middle = (low + high) // 2
        if get_key(sorted_items[middle]) >= minimum:
            result = middle
            high = middle - 1
        else:
            low = middle + 1
    return result
