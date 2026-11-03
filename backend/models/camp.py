# This file holds the camp model.

from backend.structures.linked_list import LinkedList


class Camp:
    def __init__(
        self,
        camp_id,
        name,
        district,
        capacity,
        current_occupancy=0,
    ):
        self.camp_id = camp_id
        self.name = name
        self.district = district
        self.capacity = capacity
        self.current_occupancy = current_occupancy
        self.supplies = LinkedList()

    def add_supply(self, batch):
        self.supplies.add_last(batch)

    def remove_supply(self, batch):
        return self.supplies.remove_item(batch)

    def find_supply(self, batch_id):
        supplies = self.supplies.to_list()

        for batch in supplies:
            if batch.batch_id == batch_id:
                return batch

        return None

    def remove_supply_by_id(self, batch_id):
        batch = self.find_supply(batch_id)

        if batch is None:
            return False

        return self.remove_supply(batch)

    def free_space(self):
        return self.capacity - self.current_occupancy

    def is_full(self):
        return self.current_occupancy >= self.capacity

    def supply_list(self):
        return self.supplies.to_list()
