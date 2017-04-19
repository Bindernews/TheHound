
class Result:
    def __init__(self, name, description='', length=0, *args, **kwargs):
        self.name = name
        self.length = length
        self.description = description
        self.data = dict(**kwargs)

    def __str__(self):
        s = self.name
        if self.description:
            s += ' ' + self.description
        if len(self.data) > 0:
            s += ' ' + str(self.data)
        return s
        
MEBIBYTE = 1024 * 1024
