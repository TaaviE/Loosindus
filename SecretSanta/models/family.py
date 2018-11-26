from django.db.models import Model, DateField, CharField, IntegerField, ForeignKey, CASCADE

from SecretSanta.models.group import Group


class Family(Model):
    """
    Specifies how families are modeled in the database

    @type  id: int
    @param id: family's ID
    @type  group_id: int
    @param group_id: group where the family belongs ID
    @type  name: str
    @param name: 255 letter name of the group
    """

    class Meta:
        db_table = "families"
    id = IntegerField(primary_key=True, unique=True, null=False)
    group_id = IntegerField(ForeignKey(Group, db_column='id', on_delete=CASCADE), null=False)
    name = CharField(max_length=255, null=False)
    creation = DateField(auto_now=True, blank=False, null=False)
