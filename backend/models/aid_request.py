# This file holds the aid request model.


class AidRequest:
    def __init__(
        self,
        request_id,
        area_name,
        needs,
        severity,
        created_at,
    ):
        self.request_id = request_id
        self.area_name = area_name
        self.needs = needs
        self.severity = severity
        self.created_at = created_at
