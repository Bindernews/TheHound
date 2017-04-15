
class Result:
    def __init__(self, name, length=-1, description='', *args, **kwargs):
        self.name = name
        self.length = length
        self.description = description
        for key, value in kwargs.iteritems():
        	self[key] = value
        
    