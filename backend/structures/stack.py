# This file holds a stack.


class Stack:
    # time: O(1)
    def __init__(self):
        self.items = []

    # time: O(1)
    def push(self, item):
        self.items.append(item)

    # time: O(1)
    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    # time: O(1)
    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    # time: O(1)
    def is_empty(self):
        return len(self.items) == 0

    # time: O(1)
    def size(self):
        return len(self.items)

    # time: O(n)
    def to_list(self):
        return list(self.items)
