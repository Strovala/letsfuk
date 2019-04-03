class HttpException(Exception):
    def __init__(self, text, status_code):
        super(HttpException, self).__init__(text)
        self.text = text
        self.status_code = status_code


class BadRequest(HttpException):
    def __init__(self, text):
        super(BadRequest, self).__init__(text, 400)


class NotFound(HttpException):
    def __init__(self, text):
        super(NotFound, self).__init__(text, 404)


class Conflict(HttpException):
    def __init__(self, text):
        super(Conflict, self).__init__(text, 409)


class Unauthorized(HttpException):
    def __init__(self, text):
        super(Unauthorized, self).__init__(text, 401)


class InternalError(HttpException):
    def __init__(self, text):
        super(InternalError, self).__init__(text, 500)
