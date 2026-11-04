import random
import sys
import time
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.algorithms.slow_sorts import bubble_sort, insertion_sort
from backend.algorithms.sorting import merge_sort, quick_sort


def get_number(number):
    return number


def time_sort(sort_function, values):
    start = time.perf_counter()
    sort_function(values, get_number)
    return (time.perf_counter() - start) * 1000


def main():
    random.seed(1)
    print("Results will differ between laptops.")
    print("Size | Bubble ms | Insertion ms | Merge ms | Quick ms")
    for size in (500, 1000, 2000, 4000):
        values = [random.randint(1, size) for _ in range(size)]
        bubble_time = time_sort(bubble_sort, values)
        insertion_time = time_sort(insertion_sort, values)
        merge_time = time_sort(merge_sort, values)
        quick_time = time_sort(quick_sort, values)
        print(
            str(size) + " | "
            + f"{bubble_time:.2f} | {insertion_time:.2f} | "
            + f"{merge_time:.2f} | {quick_time:.2f}"
        )


if __name__ == "__main__":
    main()
