import secretsanta.secretsanta

class ConnectionGraph:
    def __init__(self, families, members):
        self.members_to_families = families
        self.families_to_members = members
        self.vertices = {}

    def __repr__(self):
        return repr(self.vertices)

    def __iter__(self):
        for vertice in self.vertices:
            yield vertice

    def add(self, source, target, year):
        if source not in self.vertices:
            self.vertices[source] = {target: {year}}
        elif target not in self.vertices[source]:
            self.vertices[source][target] = {year}
        else:
            self.vertices[source][target].add(year)

    def has(self, source, target):
        return (source in self.vertices
                and target in self.vertices[source])

    def has_in_year(self, source, target, year):
        return (source in self.vertices
                and target in self.vertices[source]
                and year in self.vertices[source][target])

    def make_weighted_conn(self, source, target, year):

        weight = 0
        source_family = self.members_to_families[source]
        target_family = self.members_to_families[target]

        if source in self.vertices:
            for vertice in self.vertices[source]:
                if vertice in self.members_to_families and target_family == self.members_to_families[vertice]:
                    weight += len(self.vertices[source])

        if target in self.vertices:
            for vertice in self.vertices[target]:
                if vertice in self.members_to_families and source_family == self.members_to_families[vertice]:
                    weight += len(self.vertices[target])

        return secretsanta.Connection.Connection(source, target, year, weight)
