# This file holds a simple queue.


class QueueNode:
    # time: O(1)
    def __init__(self, item):
        self.item = item
        self.next = None


class Queue:
    # time: O(1)
    def __init__(self):
        self.front = None
        self.rear = None
        self.count = 0

    # time: O(1)
    def enqueue(self, item):
        new_node = QueueNode(item)

        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

        self.count += 1

    # time: O(1)
    def dequeue(self):
        if self.front is None:
            return None

        item = self.front.item
        self.front = self.front.next
        self.count -= 1

        if self.front is None:
            self.rear = None

        return item

    # time: O(1)
    def peek(self):
        if self.front is None:
            return None
        return self.front.item

    # time: O(1)
    def is_empty(self):
        return self.count == 0

    # time: O(1)
    def size(self):
        return self.count

    # time: O(n)
    def to_list(self):
        items = []
        current = self.front

        while current is not None:
            items.append(current.item)
            current = current.next

        return items
