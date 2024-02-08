
# Teste find_correlation
import datetime
from datetime import datetime

from domain.Uri import Uri as uri
from repository import MySqlRepository


def find_correlation():
    ur1 = uri(7, "teste2", "", "")
    ur2 = uri(6, "teste", "", "")
    try:
        tester = MySqlRepository.MySqlRepository.find_correlation(ur1, ur2)
        print(tester)
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))


def save_correlation():
    data1 = datetime.datetime.strptime('2022/06/27 11:55:25 +0000', '%Y/%m/%d %H:%M:%S %z')
    data2 = datetime.datetime.strptime('2022/06/27 11:56:26 +0000', '%Y/%m/%d %H:%M:%S %z')
    ur1 = uri(7, "teste1", "123", "2022/06/27 11:55:25 00:00")
    ur2 = uri(6, "teste2", "123", "2022/06/27 11:56:25 00:00")
    try:
        tester = MySqlRepository.MySqlRepository.save_correlation(ur1, ur2)
        print(tester)
        return tester
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))

def save_repeated_correlation_attributes():
    correlation_id = 1
    condition_attribute_name = "testeCondition"
    result_attribute_name = "testeResult"
    attribute_value = "valorTeste"
    try:
        tester = MySqlRepository.MySqlRepository.save_correlation_repeated_attributes(correlation_id, condition_attribute_name, result_attribute_name, attribute_value)
        print(tester)
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))

def check_uri_eq():
    ur1 = uri(7, "teste2", "22", "1")
    ur2 = uri(7, "teste2", "22", "1")
    try:
        tester = ur1.__eq__(ur2)
        print(tester)
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))

t = check_uri_eq()
print(t)


