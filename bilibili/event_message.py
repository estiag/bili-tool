class EventMessage:
    def __init__(self, message_type, message):
        self.message = message
        self.message_type = message_type

    def __str__(self):
        return f'{self.message_type}, {self.message}'
