# This file holds a linked list.


class Node:
    # time: O(1)
    def __init__(self, item):
        self.item = item
        self.next = None


class LinkedList:
    # time: O(1)
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    # time: O(1)
    def add_first(self, item):
        new_node = Node(item)
        new_node.next = self.head
        self.head = new_node

        if self.tail is None:
            self.tail = new_node

        self.count += 1

    # time: O(1)
    def add_last(self, item):
        new_node = Node(item)

        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.count += 1

    # time: O(1)
    def remove_first(self):
        if self.head is None:
            return None

        removed_item = self.head.item
        self.head = self.head.next
        self.count -= 1

        if self.head is None:
            self.tail = None

        return removed_item

    # time: O(n)
    def remove_item(self, item):
        previous = None
        current = self.head

        while current is not None:
            if current.item == item:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self.count -= 1
                return True

            previous = current
            current = current.next

        return False

    # time: O(n)
    def contains(self, item):
        current = self.head

        while current is not None:
            if current.item == item:
                return True
            current = current.next

        return False

    # time: O(1)
    def size(self):
        return self.count

    # time: O(1)
    def is_empty(self):
        return self.count == 0

    # time: O(n)
    def to_list(self):
        items = []
        current = self.head

        while current is not None:
            items.append(current.item)
            current = current.next

        return items
