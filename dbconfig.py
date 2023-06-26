class Connect:
    def __init__(self) -> None:
        self.user = ''
        self.password = ''
        self.dsn = ''
    
    def set_connection_data(self,user,password,ip,port,service_name):
        self.user = user
        self.password = password
        self.dsn = ip + ':' + port + '/' + service_name

    def get_connection_data(self):
        return self.user, self.password, self.dsn