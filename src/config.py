YOUR_API_KEY = "X74KBRFD1MUMV265BRBM4FRQ4K6UJ614GE"

class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'BscScanAPI_PasSWoRd'
    MYSQL_DB = 'BscScanAPI_DB'
    

config = {
    'development': DevelopmentConfig
}

