# For comparison only. The app does not use these.


def bubble_sort(items, get_key):
    result = list(items)
    end = len(result) - 1
    while end > 0:
        index = 0
        while index < end:
            if get_key(result[index]) > get_key(result[index + 1]):
                result[index], result[index + 1] = (
                    result[index + 1],
                    result[index],
                )
            index += 1
        end -= 1
    return result


def insertion_sort(items, get_key):
    result = list(items)
    index = 1
    while index < len(result):
        item = result[index]
        item_key = get_key(item)
        position = index - 1
        while position >= 0 and get_key(result[position]) > item_key:
            result[position + 1] = result[position]
            position -= 1
        result[position + 1] = item
        index += 1
    return result
