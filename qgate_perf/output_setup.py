
class Singleton (type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class OutputSetup(metaclass=Singleton):
    """Global setup/setting for tuning of output"""

    HUMAN_PRECISION = 4
    HUMAN_JSON_SEPARATOR = (', ', ':')
    JSON_SEPARATOR = (',', ':')

    def __init__(self):
        self._human_precision = OutputSetup.HUMAN_PRECISION
        self._human_json_separator = OutputSetup.HUMAN_JSON_SEPARATOR

    @property
    def human_precision(self):
        return self._human_precision

    @human_precision.setter
    def human_precision(self, value):
        self._human_precision = value

    @property
    def human_json_separator(self):
        return self._human_json_separator

    @human_json_separator.setter
    def human_json_separator(self, value):
        self._human_json_separator = value

    @property
    def json_separator(self):
        return OutputSetup.JSON_SEPARATOR

