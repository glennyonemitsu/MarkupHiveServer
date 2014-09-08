class APIError(StandardError):

    def __init__(self, errors):
        if isinstance(errors, str) or isinstance(errors, unicode):
            errors = [errors]
        self.errors = errors

