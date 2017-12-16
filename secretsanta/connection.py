
class Connection:

    def __init__(self, source, target, year, weight = 0):
        self.source = source
        self.target = target
        self.year   = year
        self.weight = weight

    def __str__(self):
        return "{}|{}|{}|{}".format(self.source,
                                    self.target,
                                    self.year,
                                    self.weight)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.source,
                     self.target,
                     self.year))

    def reverse(self):
        return Connection(self.target,
                          self.source,
                          self.year,
                          self.weight)

