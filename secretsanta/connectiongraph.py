from connection import Connection

class ConnectionGraph:

    def __init__(self, families, members):
        self.families = families
        self.members = members
        self.vertices = {}

    def __repr__(self):
        return repr(self.vertices)

    def add(self, source, target, year):
        if source not in self.vertices:
            self.vertices[source] = { target: set([year]) }
        elif target not in self.vertices[source]:
            self.vertices[source][target] = set([year])
        else:
            self.vertices[source][target].add(year)
        
    def has(self, source, target):
        return (source in self.vertices
           and  target in self.vertices[source])

    def hasInYear(self, source, target, year):
        return (source in self.vertices
           and  target in self.vertices[source]
           and  year   in self.vertices[source][target])

    def makeWeightedConn(self, source, target, year):

        weight = 0
        sourceFam = self.families[source]        
        targetFam = self.families[target]

        if source in self.vertices:
            for v in self.vertices[source]:
                if v in self.families and targetFam == self.families[v]:
                    weight += len(self.vertices[source])

        if target in self.vertices:
            for v in self.vertices[target]:
                if v in self.families and sourceFam == self.families[v]:
                    weight += len(self.vertices[target])

        return Connection(source, target, year, weight)
