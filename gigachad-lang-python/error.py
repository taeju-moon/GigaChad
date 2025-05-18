class ErrorMessage:
    def __init__(
        self,
        UserName,
        FormatException,
        InterpretFailException,
        ValueNotDefinedException,
        InvalidValueException,
        ValueAlreadyDefinedException,
    ):
        self.UserName: str = UserName
        self.FormatException: str = FormatException
        self.InterpretFailException: str = InterpretFailException
        self.ValueNotDefinedException: str = ValueNotDefinedException
        self.InvalidValueException: str = InvalidValueException
        self.ValueAlreadyDefinedException: str = ValueAlreadyDefinedException

    def get_format_exception(self):
        return self.FormatException.replace("[USERNAME]", self.UserName)

    def get_interpret_fail_exception(self, line):
        return self.InterpretFailException.replace("[USERNAME]", self.UserName).replace("[LINE]", line)

    def get_value_not_defined_exception(self, value):
        return self.ValueNotDefinedException.replace("[USERNAME]", self.UserName).replace("[VALUE]", value)

    def get_invalid_value_exception(self, value1, value2):
        return self.InvalidValueException.replace("[USERNAME]", self.UserName).replace("[VALUE1]", value1).replace("[VALUE2]", value2)

    def get_value_already_defined_exception(self, value):
        return self.ValueAlreadyDefinedException.replace("[USERNAME]", self.UserName).replace("[VALUE]", value)
