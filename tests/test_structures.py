# This file tests the linear structures.

import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.logging_tools.audit_logger import AuditLogger
from backend.models.aid_request import AidRequest
from backend.models.camp import Camp
from backend.models.supply_batch import SupplyBatch
from backend.services.request_service import RequestService
from backend.services.undo_manager import UndoManager
from backend.services.undo_service import UndoService
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
    check("new list is empty", linked_list.is_empty())
    linked_list.add_first("second")
    linked_list.add_first("first")
    linked_list.add_last("third")
    check(
        "linked list order",
        linked_list.to_list() == ["first", "second", "third"],
    )
    check("linked list size", linked_list.size() == 3)
    check("linked list contains", linked_list.contains("second"))
    check("linked list remove head", linked_list.remove_item("first"))
    check("linked list remove middle", linked_list.remove_item("second"))
    check("linked list remove last", linked_list.remove_item("third"))
    check("list empty after removals", linked_list.is_empty())
    linked_list.add_last("new last")
    check("tail works after removing last", linked_list.to_list() == ["new last"])
    check("remove only item", linked_list.remove_first() == "new last")
    linked_list.add_last("again")
    check("add after removing only item", linked_list.to_list() == ["again"])
    check("linked list remove first", linked_list.remove_first() == "again")

    stack = Stack()
    check("new stack is empty", stack.is_empty())
    stack.push("first")
    stack.push("second")
    check("stack size", stack.size() == 2)
    check("stack peek", stack.peek() == "second")
    check("stack to list", stack.to_list() == ["first", "second"])
    check("stack last in first out", stack.pop() == "second")
    check("stack pop returns first item", stack.pop() == "first")
    check("stack empty pop", stack.pop() is None)
    check("stack empty after pop", stack.is_empty())

    queue = Queue()
    check("new queue is empty", queue.is_empty())
    queue.enqueue("first")
    queue.enqueue("second")
    check("queue size", queue.size() == 2)
    check("queue peek", queue.peek() == "first")
    check("queue to list", queue.to_list() == ["first", "second"])
    check("queue first in first out", queue.dequeue() == "first")
    check("queue second item", queue.dequeue() == "second")
    check("queue empty dequeue", queue.dequeue() is None)
    check("queue empty after dequeue", queue.is_empty())

    camp = Camp(1, "Test Camp", "Dadu", 100, 40)
    first_supply = SupplyBatch(1, "Water", 20, 10)
    second_supply = SupplyBatch(2, "Food", 15, 20)
    camp.add_supply(first_supply)
    camp.add_supply(second_supply)
    check("camp supply add", camp.supply_list() == [first_supply, second_supply])
    check("camp find supply", camp.find_supply(2) == second_supply)
    check("camp missing supply", camp.find_supply(99) is None)
    check("camp supply remove by id", camp.remove_supply_by_id(1))
    check("camp supply remove", camp.remove_supply(second_supply))
    check("camp free space", camp.free_space() == 60)
    check("camp is not full", not camp.is_full())
    full_camp = Camp(2, "Full Camp", "Dadu", 10, 10)
    check("full camp", full_camp.is_full())

    test_log = PROJECT_FOLDER / "logs" / "test_audit.log"
    audit_logger = AuditLogger(log_file=test_log)
    request_service = RequestService(audit_logger, use_database=False)
    first_request = AidRequest(1, "Area 1", "Water", 3, "12:00")
    second_request = AidRequest(2, "Area 2", "Food", 4, "12:01")
    request_service.add_request(first_request)
    request_service.add_request(second_request)
    check("request waiting count", request_service.waiting_count() == 2)
    check(
        "request waiting order",
        request_service.waiting_requests() == [first_request, second_request],
    )
    check("serve empty request", RequestService(
        audit_logger,
        use_database=False,
    ).serve_next() is None)
    check("request service arrival order", request_service.serve_next() == first_request)
    check("request service second request", request_service.serve_next() == second_request)

    undo_manager = UndoManager(audit_logger)
    check("undo cannot undo at start", not undo_manager.can_undo())
    undo_manager.record_action("ADD_ROAD", "road-1", "Added first road")
    undo_manager.record_action("BLOCK_ROAD", "road-1", "Blocked first road")
    check("undo can undo after record", undo_manager.can_undo())
    newest_action = undo_manager.undo_last()
    check("undo newest action", newest_action["action_name"] == "BLOCK_ROAD")
    check("undo next action", undo_manager.undo_last()["action_name"] == "ADD_ROAD")
    check("undo empty after actions", not undo_manager.can_undo())
    undo_manager.record_action("ADD_CAMP", "1", "Camp one")
    undo_manager.record_action("ADD_SUPPLY", "2", "Water")
    check("undo peek newest", undo_manager.peek_last()["target"] == "2")
    check(
        "undo history newest first",
        [record["target"] for record in undo_manager.history()] == ["2", "1"],
    )
    check("undo count", undo_manager.count() == 2)
    undo_manager.clear()
    check("undo clear", undo_manager.count() == 0)
    undo_manager.record_action("SOMETHING_ELSE", "abc", "Unknown action")
    undo_service = UndoService(undo_manager, audit_logger)
    unknown_result = undo_service.perform_undo()
    check(
        "unknown undo action message",
        unknown_result == {"message": "This action cannot be undone"},
    )
    check("unknown undo action removed", undo_manager.count() == 0)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
