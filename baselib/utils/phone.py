import phonenumbers


class PhoneNumber:
    def __init__(self):
        pass

    @staticmethod
    def _separate_multiple(phone):
        separator = [x for x in ";,/:"]
