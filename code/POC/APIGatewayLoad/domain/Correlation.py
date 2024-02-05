class Correlation:
    id = None
    antecedent_id = None
    consequent_id = None
    quantity = 0

    def __init__(self, _id, antecedent_id, consequent_id, quantity):
        self.id = _id
        self.antecedent_id = antecedent_id
        self.consequent_id = consequent_id
        self.quantity = quantity

    def get_id(self):
        return self.id

    def get_antecedent_id(self) -> str:
        return self.antecedent_id

    def get_consequent_id(self):
        return self.consequent_id

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity: int):
        self.quantity = quantity



