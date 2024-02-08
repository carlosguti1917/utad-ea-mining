import re

class Uri:
    id = None
    uri = None
    client_id = None
    request_timestamp = None
    method = None
    operation_path = None
    operation_identifier = None
    service_destination = None

    def __init__(self, _id, uri, client_id, method, operation_path, request_timestamp):
            self.id = _id
            self.uri = uri
            self.client_id = client_id
            self.method = method
            self.request_timestamp = request_timestamp
            #reg_pattern = '(\/[0-9]+\/?)'
            #re.compile(reg_pattern)
            if operation_path is not None:
                self.operation_path = operation_path
                self.operation_identifier = method + " " + operation_path

    def get_id(self):
        return self.id

    def set_id(self, _id):
         self.id = _id

    def get_uri(self) -> str:
        return self.uri

    def get_client_id(self):
        return self.client_id

    def get_request_timestamp(self):
        return self.request_timestamp

    def get_method(self):
        return self.method

    def get_operation_path(self):
        return self.operation_path

    def set_operation_path(self, path):
        self.operation_path = path
        if self.method is not None:
            self.operation_identifier = self.method + " " + path

    def get_operation_identifier(self):
        return self.operation_identifier

    def __eq__(self, other):
        ret = False
        if isinstance(other, Uri):
            ret = (self.uri, self.client_id, self.method, self.request_timestamp) == (other.uri, other.client_id, other.method, other.request_timestamp)
        return ret

    def is_valid(self) -> bool:
        #Verifica se instância é valida e possui os campos obrigatórios
        if self.uri is None or str.isspace(self.uri) or self.client_id is None or str.isspace(self.client_id) or str.isspace(self.method) or self.request_timestamp is None or str.isspace(self.request_timestamp):
            return False
        else:
            return True
