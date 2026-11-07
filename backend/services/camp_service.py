import time

from backend.algorithms.searching import binary_search, first_index_at_least
from backend.algorithms.sorting import merge_sort, quick_sort
from backend.database import camp_repository
from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger


def get_camp_name(camp):
    return camp.name.lower()


def get_capacity(camp):
    return camp.capacity


def get_free_space(camp):
    return camp.free_space()


class CampService:
    def __init__(self, camps, audit_logger=None):
        self.camps = camps
        if audit_logger is None:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = audit_logger

    def sort_camps(self, field, order, algorithm):
        keys = {
            "name": get_camp_name,
            "capacity": get_capacity,
            "free_space": get_free_space,
        }
        get_key = keys[field]
        descending = order == "desc"
        start = time.perf_counter()
        if algorithm == "merge":
            sorted_camps = merge_sort(self.camps, get_key, descending)
        else:
            sorted_camps = quick_sort(self.camps, get_key, descending)
        milliseconds = (time.perf_counter() - start) * 1000
        self.audit_logger.log_action(
            "admin",
            ActionNames.SORT_CAMPS,
            field,
            "Camps sorted",
        )
        return sorted_camps, milliseconds

    def find_camp_with_free_space(self, minimum):
        sorted_camps = merge_sort(self.camps, get_free_space)
        index = first_index_at_least(sorted_camps, get_free_space, minimum)
        self.audit_logger.log_action(
            "admin",
            ActionNames.FIND_CAMP,
            str(minimum),
            "Camp searched by free space",
        )
        if index == -1:
            return None
        return sorted_camps[index]

    def find_camp_by_name(self, name):
        sorted_camps = merge_sort(self.camps, get_camp_name)
        index = binary_search(sorted_camps, get_camp_name, name.lower())
        self.audit_logger.log_action(
            "admin",
            ActionNames.FIND_CAMP,
            name,
            "Camp searched by name",
        )
        if index == -1:
            return None
        return sorted_camps[index]

    def register_arrival(self, camp_id, people):
        camp = self._load_camp(camp_id)
        if camp is None:
            return None
        if people > camp.free_space():
            return {
                "ok": False,
                "message": "Camp has only " + str(camp.free_space())
                + " free places",
            }
        return self._change_occupancy(camp, people, ActionNames.REGISTER_ARRIVAL)

    def register_departure(self, camp_id, people):
        camp = self._load_camp(camp_id)
        if camp is None:
            return None
        if people > camp.current_occupancy:
            return {
                "ok": False,
                "message": "Camp has only " + str(camp.current_occupancy)
                + " people registered",
            }
        return self._change_occupancy(
            camp,
            -people,
            ActionNames.REGISTER_DEPARTURE,
        )

    def _load_camp(self, camp_id):
        return camp_repository.load_camp(camp_id)

    def _change_occupancy(self, camp, change, action):
        changed = camp_repository.change_occupancy(camp.camp_id, change)
        if not changed:
            return {
                "ok": False,
                "message": "Could not update the camp, please try again",
            }
        if action == ActionNames.REGISTER_ARRIVAL:
            message = (
                "Registered " + str(change) + " arrivals at " + camp.name
                + ". Free places: " + str(camp.free_space() - change)
            )
        else:
            message = (
                "Registered " + str(-change) + " departures at " + camp.name
                + ". Free places: " + str(camp.free_space() - change)
            )
        self.audit_logger.log_action("admin", action, str(camp.camp_id), message)
        return {"ok": True, "message": message}
