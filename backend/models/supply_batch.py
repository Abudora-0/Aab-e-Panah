# This file holds the supply batch model.


class SupplyBatch:
    def __init__(self, batch_id, item_name, quantity, expiry_days):
        self.batch_id = batch_id
        self.item_name = item_name
        self.quantity = quantity
        self.expiry_days = expiry_days
