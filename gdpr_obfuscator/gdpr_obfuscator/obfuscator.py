class Obfuscator:
    """
    """
    def __init__(self, pii_fields:list = None):
        if pii_fields is None:
            pii_fields = []
        self.__pii_fields = pii_fields

    @property
    def pii_fields(self):
        return self.__pii_fields
    
    @pii_fields.setter
    def pii_fields(self, value:list):
        self.__pii_fields = value