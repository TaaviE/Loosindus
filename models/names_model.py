from main import db


class Name(db.Model):
    """
    Specifies how names are stored in the database for Estonian localization

    @param name: the name as a string
    @type  name: str
    @param genitive: the name in genitive case
    @type genitive: str
    """
    __tablename__ = "names_cases"

    name = db.Column(db.VARCHAR(255), primary_key=True, nullable=False)
    genitive = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self, name, genitive):
        self.name = name
        self.genitive = genitive

    def __repr__(self):
        return "<id {}>".format(self.id)

    def __str__(self):
        return "{\"name\": \"{name}\", \"genitive\": \"{genitive}\"}".format(name=self.name, genitive=self.genitive)
