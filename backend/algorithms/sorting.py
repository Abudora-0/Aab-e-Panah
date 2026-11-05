def counting_sort_by_severity(requests, descending=True):
    # time: O(n), extra space: O(n)
    counts = [0, 0, 0, 0, 0]
    for request_item in requests:
        counts[request_item.severity - 1] += 1

    starts = [0, 0, 0, 0, 0]
    if descending:
        position = 0
        severity = 5
        while severity >= 1:
            starts[severity - 1] = position
            position += counts[severity - 1]
            severity -= 1
    else:
        position = 0
        severity = 1
        while severity <= 5:
            starts[severity - 1] = position
            position += counts[severity - 1]
            severity += 1

    result = [None] * len(requests)
    next_positions = list(starts)
    for request_item in requests:
        severity_index = request_item.severity - 1
        result[next_positions[severity_index]] = request_item
        next_positions[severity_index] += 1
    return result


def _merge(left, right, get_key, descending):
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        left_key = get_key(left[left_index])
        right_key = get_key(right[right_index])
        take_left = left_key <= right_key
        if descending:
            take_left = left_key >= right_key
        if take_left:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1
    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1
    return merged


def _merge_sort(items, get_key, descending):
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = _merge_sort(items[:middle], get_key, descending)
    right = _merge_sort(items[middle:], get_key, descending)
    return _merge(left, right, get_key, descending)


def merge_sort(items, get_key, descending=False):
    # time: O(n log n), extra space: O(n)
    return _merge_sort(list(items), get_key, descending)


def _partition_three_way(items, low, high, get_key, descending):
    middle = (low + high) // 2
    pivot_key = get_key(items[middle])
    before = low
    current = low
    after = high

    while current <= after:
        current_key = get_key(items[current])
        if descending:
            is_before = current_key > pivot_key
            is_after = current_key < pivot_key
        else:
            is_before = current_key < pivot_key
            is_after = current_key > pivot_key

        if is_before:
            items[before], items[current] = items[current], items[before]
            before += 1
            current += 1
        elif is_after:
            items[current], items[after] = items[after], items[current]
            after -= 1
        else:
            current += 1

    return before, after


def _quick_sort(items, low, high, get_key, descending):
    if low >= high:
        return
    equal_start, equal_end = _partition_three_way(
        items,
        low,
        high,
        get_key,
        descending,
    )
    _quick_sort(items, low, equal_start - 1, get_key, descending)
    _quick_sort(items, equal_end + 1, high, get_key, descending)


def quick_sort(items, get_key, descending=False):
    # time: O(n log n) average with equal values handled, extra space: O(log n)
    result = list(items)
    _quick_sort(result, 0, len(result) - 1, get_key, descending)
    return result
