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
        if action_name == ActionNames.ADD_CAMP:
            return self._undo_record(
                record,
                camp_repository.delete_camp,
                "Undid: added camp ",
                "Camp was already gone",
            )
        if action_name == ActionNames.ADD_SUPPLY:
            return self._undo_record(
                record,
                supply_repository.delete_supply,
                "Undid: added supply ",
                "Supply was already gone",
            )
        self.undo_manager.undo_last()
        return {"message": "This action cannot be undone"}

    def _undo_record(self, record, delete_function, success_prefix, gone_message):
        target = int(record["target"])
        try:
            deleted = delete_function(target)
        except mysql.connector.Error as error:
            self.audit_logger.log_error(
                "admin",
                ActionNames.UNDO_ACTION,
                record["target"],
                str(error),
            )
            raise
        self.undo_manager.undo_last()
        if deleted:
            return {"message": success_prefix + record["details"]}
        return {"message": gone_message}
