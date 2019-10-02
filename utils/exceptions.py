class UnauthorizedException(Exception):
    def __init__(self):
        super(UnauthorizedException, self).__init__('User not authenticated.')


class ForbiddenException(Exception):
    def __init__(self):
        super(ForbiddenException, self).__init__('User not authorized.')


class ConflictException(Exception):
    def __init__(self):
        super(ConflictException, self).__init__('Request creates conflict.')


class NotFoundException(Exception):
    def __init__(self):
        super(NotFoundException, self).__init__('Request requires a resource which can not be found.')
