# This file holds names for audit actions.


class ActionNames:
    ADD_CAMP = "ADD_CAMP"
    UPDATE_CAMP = "UPDATE_CAMP"
    ADD_ROAD = "ADD_ROAD"
    BLOCK_ROAD = "BLOCK_ROAD"
    UNBLOCK_ROAD = "UNBLOCK_ROAD"
    ADD_REQUEST = "ADD_REQUEST"
    SERVE_REQUEST = "SERVE_REQUEST"
    UNDO_ACTION = "UNDO_ACTION"
    RUN_ROUTE = "RUN_ROUTE"
    SORT_CAMPS = "SORT_CAMPS"
    FIND_CAMP = "FIND_CAMP"
    RANK_REQUESTS = "RANK_REQUESTS"
    ADD_SUPPLY = "ADD_SUPPLY"
    ISSUE_SUPPLIES = "ISSUE_SUPPLIES"
    REGISTER_ARRIVAL = "REGISTER_ARRIVAL"
    REGISTER_DEPARTURE = "REGISTER_DEPARTURE"
    SYSTEM_ERROR = "SYSTEM_ERROR"

    @staticmethod
    def all_names():
        return [
            ActionNames.ADD_CAMP,
            ActionNames.UPDATE_CAMP,
            ActionNames.ADD_ROAD,
            ActionNames.BLOCK_ROAD,
            ActionNames.UNBLOCK_ROAD,
            ActionNames.ADD_REQUEST,
            ActionNames.SERVE_REQUEST,
            ActionNames.UNDO_ACTION,
            ActionNames.RUN_ROUTE,
            ActionNames.SORT_CAMPS,
            ActionNames.FIND_CAMP,
            ActionNames.RANK_REQUESTS,
            ActionNames.ADD_SUPPLY,
            ActionNames.ISSUE_SUPPLIES,
            ActionNames.REGISTER_ARRIVAL,
            ActionNames.REGISTER_DEPARTURE,
            ActionNames.SYSTEM_ERROR,
        ]
