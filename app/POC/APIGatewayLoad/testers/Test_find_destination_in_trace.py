import unittest

import Service.EventBuildArango as eb

trace = ""


class Test_find_destination_in_trance():

    a = eb.get_api_destination_in_trace(trace)
    print(str(a))

if __name__ == '__main__':
    Test_find_destination_in_trance()
