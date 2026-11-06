import mysql.connector

from backend.database import camp_repository
from backend.database import supply_repository
from backend.logging_tools.action_names import ActionNames


class UndoService:
    def __init__(self, undo_manager, audit_logger):
        self.undo_manager = undo_manager
        self.audit_logger = audit_logger

    def perform_undo(self):
        record = self.undo_manager.peek_last()
        if record is None:
            return None

        action_name = record["action_name"]
        target = int(record["target"])
        if action_name == ActionNames.ADD_CAMP:
            try:
                deleted = camp_repository.delete_camp(target)
            except mysql.connector.Error as error:
                self.audit_logger.log_error(
                    "admin",
                    ActionNames.UNDO_ACTION,
                    record["target"],
                    str(error),
                )
                raise
            if deleted:
                self.undo_manager.undo_last()
                return {"message": "Undid: added camp " + record["details"]}
            self.undo_manager.undo_last()
            return {"message": "Camp was already gone"}
        if action_name == ActionNames.ADD_SUPPLY:
            try:
                deleted = supply_repository.delete_supply(target)
            except mysql.connector.Error as error:
                self.audit_logger.log_error(
                    "admin",
                    ActionNames.UNDO_ACTION,
                    record["target"],
                    str(error),
                )
                raise
            if deleted:
                self.undo_manager.undo_last()
                return {"message": "Undid: added supply " + record["details"]}
            self.undo_manager.undo_last()
            return {"message": "Supply was already gone"}
        self.undo_manager.undo_last()
        return {"message": "Nothing to undo"}
