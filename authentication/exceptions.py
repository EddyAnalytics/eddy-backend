class UserNotAuthenticatedException(Exception):
    def __init__(self):
        super(UserNotAuthenticatedException, self).__init__('User not authenticated.')


class UserNotAuthorizedException(Exception):
    def __init__(self):
        super(UserNotAuthorizedException, self).__init__('User not authorized.')
