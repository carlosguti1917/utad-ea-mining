
class OperationUriCorrelation:
    id = None
    key = None
    from_ = None
    to_ = None
    node = None
    quantity = 0
    weigth = 0

    def __init__(self, _id, _from, _to, node):
        self.id = _id
        self.from_ = _from
        self.to_ = _to
        self.node = node

    def get_id(self):
        return self.id

    def get_from(self) -> str:
        return self.from_

    def get_to(self):
        return self.to_

    def get_node(self):
        return self.node

    def get_quantity(self):
        return self.quantity

    def set_id(self, _id):
        self.id = _id

    def set_quantity(self, quantity: int):
        self.quantity = quantity

    def get_weigth(self):
        return self.weigth

    def set_weigth(self, weigth: int):
        self.weigth = weigth

