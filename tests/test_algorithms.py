import random
import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.algorithms.searching import binary_search, first_index_at_least
from backend.algorithms.sorting import (
    counting_sort_by_severity,
    merge_sort,
    quick_sort,
)
from backend.models.aid_request import AidRequest


failures = 0


def identity(item):
    return item


def pair_key(item):
    return item[0]


def check(label, condition):
    global failures
    if condition:
        print("PASS:", label)
    else:
        print("FAIL:", label)
        failures += 1


def main():
    requests = [
        AidRequest(1, "one", "water", 3, ""),
        AidRequest(2, "two", "food", 5, ""),
        AidRequest(3, "three", "tents", 5, ""),
        AidRequest(4, "four", "food", 1, ""),
    ]
    ranked = counting_sort_by_severity(requests)
    check("counting sort descending", [item.severity for item in ranked] == [5, 5, 3, 1])
    check("counting sort stable", [item.request_id for item in ranked[:2]] == [2, 3])
    check("counting sort empty", counting_sort_by_severity([]) == [])
    check("counting sort one item", counting_sort_by_severity(requests[:1]) == requests[:1])
    same = [AidRequest(index, str(index), "", 2, "") for index in range(4)]
    check("counting sort same severity", counting_sort_by_severity(same) == same)

    random.seed(1)
    for descending in (False, True):
        for size in (0, 1, 2, 10, 200):
            values = [random.randint(1, 20) for _ in range(size)]
            original = list(values)
            expected = sorted(values, reverse=descending)
            check("merge sort matches sorted", merge_sort(values, identity, descending) == expected)
            check("quick sort matches sorted", quick_sort(values, identity, descending) == expected)
            check("sort keeps input", values == original)
    check("merge sort duplicates stable", merge_sort([(1, "a"), (1, "b")], pair_key) == [(1, "a"), (1, "b")])

    values = [1, 3, 5, 7, 9]
    check("binary search start", binary_search(values, identity, 1) == 0)
    check("binary search middle", binary_search(values, identity, 5) == 2)
    check("binary search end", binary_search(values, identity, 9) == 4)
    check("binary search missing", binary_search(values, identity, 4) == -1)
    check("binary search empty", binary_search([], identity, 4) == -1)
    check("first at least between", first_index_at_least(values, identity, 4) == 2)
    check("first at least below", first_index_at_least(values, identity, 0) == 0)
    check("first at least above", first_index_at_least(values, identity, 10) == -1)
    check("first at least duplicate", first_index_at_least([1, 3, 3, 4], identity, 3) == 1)
    check("first at least empty", first_index_at_least([], identity, 1) == -1)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
