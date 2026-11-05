from backend.database import camp_repository
from backend.database import supply_repository
from backend.logging_tools.action_names import ActionNames


class UndoService:
    def __init__(self, undo_manager, audit_logger):
        self.undo_manager = undo_manager
        self.audit_logger = audit_logger

    def perform_undo(self):
        record = self.undo_manager.undo_last()
        if record is None:
            return None

        action_name = record["action_name"]
        target = int(record["target"])
        if action_name == ActionNames.ADD_CAMP:
            deleted = camp_repository.delete_camp(target)
            if deleted:
                return {"message": "Undid: added camp " + record["details"]}
            return {"message": "Camp was already gone"}
        if action_name == ActionNames.ADD_SUPPLY:
            deleted = supply_repository.delete_supply(target)
            if deleted:
                return {"message": "Undid: added supply " + record["details"]}
            return {"message": "Supply was already gone"}
        return {"message": "Nothing to undo"}
