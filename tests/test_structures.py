# This file tests the linear structures.

import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.models.aid_request import AidRequest
from backend.models.camp import Camp
from backend.models.supply_batch import SupplyBatch
from backend.services.request_service import RequestService
from backend.services.undo_manager import UndoManager
from backend.structures.linked_list import LinkedList
from backend.structures.simple_queue import Queue
from backend.structures.stack import Stack


failures = 0


def check(label, condition):
    global failures

    if condition:
        print("PASS:", label)
    else:
        print("FAIL:", label)
        failures += 1


def main():
    linked_list = LinkedList()
    linked_list.add_first("second")
    linked_list.add_first("first")
    linked_list.add_last("third")
    check(
        "linked list order",
        linked_list.to_list() == ["first", "second", "third"],
    )
    check("linked list remove first", linked_list.remove_first() == "first")
    check("linked list remove item", linked_list.remove_item("third"))
    check("linked list contains", linked_list.contains("second"))
    check("linked list size", linked_list.size() == 1)

    stack = Stack()
    stack.push("first")
    stack.push("second")
    check("stack last in first out", stack.pop() == "second")
    check("stack pop on empty", stack.pop() == "first")
    check("stack empty pop", stack.pop() is None)

    queue = Queue()
    queue.enqueue("first")
    queue.enqueue("second")
    check("queue first in first out", queue.dequeue() == "first")
    check("queue second item", queue.dequeue() == "second")
    check("queue empty dequeue", queue.dequeue() is None)

    camp = Camp(1, "Test Camp", "Dadu", 100)
    first_supply = SupplyBatch(1, "Water", 20, 10)
    second_supply = SupplyBatch(2, "Food", 15, 20)
    camp.add_supply(first_supply)
    camp.add_supply(second_supply)
    check("camp supply add", camp.supply_list() == [first_supply, second_supply])
    check("camp supply remove", camp.remove_supply(first_supply))
    check("camp supply left", camp.supply_list() == [second_supply])

    request_service = RequestService()
    first_request = AidRequest(1, "Area 1", "Water", 3, "12:00")
    second_request = AidRequest(2, "Area 2", "Food", 4, "12:01")
    request_service.add_request(first_request)
    request_service.add_request(second_request)
    check("request service arrival order", request_service.serve_next() == first_request)
    check("request service second request", request_service.serve_next() == second_request)

    undo_manager = UndoManager()
    undo_manager.record_action("ADD_ROAD", "road-1", "Added first road")
    undo_manager.record_action("BLOCK_ROAD", "road-1", "Blocked first road")
    newest_action = undo_manager.undo_last()
    check("undo newest action", newest_action["action_name"] == "BLOCK_ROAD")
    check("undo next action", undo_manager.undo_last()["action_name"] == "ADD_ROAD")

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
