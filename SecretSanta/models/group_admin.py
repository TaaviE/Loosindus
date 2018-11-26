from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, CASCADE, IntegerField, BooleanField

from SecretSanta.models.group import Group


class GroupAdmin(Model):
    """
    Specifies how user-group-admin relationships are modeled in the database

    @type  user_id: int
    @param user_id: user's ID
    @type  group_id: int
    @param group_id: family_id where the family belongs ID
    @type  admin: bool
    @param admin: if the user is the adming of the group
    """

    class Meta:
        db_table = "groupadmins"

    user_id = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), primary_key=True, unique=True,
                           null=False, blank=True)
    group_id = IntegerField(ForeignKey(Group, db_column='id', on_delete=CASCADE), null=False, blank=True)
    admin = BooleanField(null=False, blank=True)
