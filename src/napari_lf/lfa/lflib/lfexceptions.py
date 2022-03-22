class ZeroImageException(Exception):
    pass

class ParameterError(Exception):
    def __init__(self, message="One or more of your input parameters were invalid."):
        self.message = message
        super().__init__(self.message)

class ParameterExistsError(Exception):
    def __init__(self, parameter, message="Your parameter is invalid."):
        self.parameter = parameter
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.parameter} -> {self.message}'