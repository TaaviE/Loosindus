from django.db.models import Model, CharField, IntegerField, DateField


class Group(Model):
    """
    Specifies how groups are modeled in the database

    @type  id: int
    @param id: group's ID
    @type  description: str
    @param description: 255 letter name of the group
    """

    class Meta:
        db_table = "groups"
    id = IntegerField(null=False, blank=True, primary_key=True)
    description = CharField(max_length=255, null=True, blank=False)
    creation = DateField(auto_now=True, blank=False, null=False)
