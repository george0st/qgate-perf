
class RunReturn:
    """Wrapper for return data from executor"""
    def __init__(self, return_key, return_dict):
        self._return_key=return_key
        self._return_dict=return_dict


    @property
    def probe(self):
        return self._return_dict[self._return_key]

    @probe.setter
    def probe(self, ret):
       self._return_dict[self._return_key]=ret
