from backend.algorithms.sorting import merge_sort
from backend.database import camp_repository
from backend.database import supply_repository
from backend.logging_tools.action_names import ActionNames
from backend.models.supply_batch import SupplyBatch


def get_expiry_days(batch):
    return batch.expiry_days


class SupplyService:
    def __init__(self, undo_manager, audit_logger):
        self.undo_manager = undo_manager
        self.audit_logger = audit_logger

    def load_camp_with_supplies(self, camp_id):
        camp = camp_repository.load_camp(camp_id)
        if camp is None:
            return None
        batches = supply_repository.load_supplies_for_camp(camp_id)
        for batch in batches:
            camp.add_supply(batch)
        return camp

    def add_supply(self, camp_id, item_name, quantity, expiry_days):
        camp = camp_repository.load_camp(camp_id)
        if camp is None:
            return None
        batch_id = supply_repository.insert_supply(
            camp_id,
            item_name,
            quantity,
            expiry_days,
        )
        batch = SupplyBatch(batch_id, item_name, quantity, expiry_days)
        camp.add_supply(batch)
        details = item_name + " for " + camp.name
        self.undo_manager.record_action(
            ActionNames.ADD_SUPPLY,
            str(batch_id),
            details,
        )
        self.audit_logger.log_action(
            "admin",
            ActionNames.ADD_SUPPLY,
            str(batch_id),
            details,
        )
        return batch

    def issue_supplies(self, camp_id, item_name, amount):
        camp = self.load_camp_with_supplies(camp_id)
        if camp is None:
            return None

        matching = []
        total = 0
        for batch in camp.supply_list():
            if batch.item_name.lower() == item_name.lower():
                matching.append(batch)
                total += batch.quantity

        if total < amount:
            message = (
                "Not enough " + item_name + ": only " + str(total)
                + " available"
            )
            return {"ok": False, "message": message}

        matching = merge_sort(matching, get_expiry_days)
        remaining = amount
        updates = []
        deletions = []
        used = 0
        for batch in matching:
            if remaining == 0:
                break
            used += 1
            if batch.quantity <= remaining:
                remaining -= batch.quantity
                camp.remove_supply(batch)
                deletions.append(batch.batch_id)
            else:
                batch.quantity -= remaining
                remaining = 0
                updates.append((batch.batch_id, batch.quantity))

        supply_repository.apply_supply_changes(updates, deletions)
        self.undo_manager.clear()
        self.audit_logger.log_action(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            str(camp_id),
            "Issued " + str(amount) + " " + item_name,
        )
        return {
            "ok": True,
            "message": "Issued " + str(amount) + " " + item_name,
            "batches_used": used,
        }
