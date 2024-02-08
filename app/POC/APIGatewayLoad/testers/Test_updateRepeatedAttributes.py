import unittest

import repository.ArangodbRepository as arangodb

class Test_updateRepeatedAttributes():
    id = "Operation_Uri_Correlation/2104061"
    antecedent_attribute_name = "antecedent_teste5"
    consequent_attribute_name = "consequent_teste5"
    attribute_value = "teste5"

    arangodb.ArangodbRepository.save_correlation_repeated_attributes(id, antecedent_attribute_name, consequent_attribute_name, attribute_value)


if __name__ == '__main__':
    #unittest.main()
    Test_updateRepeatedAttributes()
