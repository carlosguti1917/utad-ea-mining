import unittest

import repository.ArangodbRepository as ar


_id = "Operation_Uri_Correlation/2343440"
antecedent = "operationId"
consequent = "operationId"
value = 17020

class Test_repeated_attributes():

    a = ar.ArangodbRepository.get_correlation_repeated_attributes(_id, antecedent, consequent, value)
    print(str(a))

if __name__ == '__main__':
    Test_repeated_attributes()
