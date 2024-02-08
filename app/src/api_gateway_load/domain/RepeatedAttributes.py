class ReapeatedAttributes:
    correlation_id = None
    antecedent_attribute_name = ""
    consequent_attribute_name = ""
    attribute_value = ""
    quantity = 0
    probability = 0

    def __init__(self, correlation_id, antecedent_attribute_name, consequent_attribute_name, attribute_value):
        self.correlation_id = correlation_id
        self.antecedent_attribute_name = antecedent_attribute_name
        self.consequent_attribute_name = consequent_attribute_name
        self.attribute_value = attribute_value

    def get_correlation_id(self):
        return self.correlation_id

    def get_condition_attribute_name(self):
        return self.antecedent_attribute_name

    def get_result_attribute_name(self):
        return self.consequent_attribute_name

    def get_attribute_value(self):
        return self.attribute_value

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, qt):
        self.quantity = qt

