class UserAlreadyExist(Exception):
    pass


class FileDoesNotExist(Exception):
    pass

class FieldError(Exception):
    def __init__(self, field: str = '', *args, **kwargs):
        if field:
            self.message = f'Field {field} is required'
        else:
            self.message = 'Field error'
        
        super().__init__(self.message, *args, **kwargs)