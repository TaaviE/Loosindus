from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, CASCADE, IntegerField, BooleanField

from SecretSanta.models.family import Family


class FamilyAdmin(Model):
    """
    Specifies how user-family-admin relationships are modeled in the database

    @type  user_id: int
    @param user_id: user's ID
    @type  family_id: int
    @param family_id: family_id where the family belongs ID
    @type  admin: bool
    @param admin: if the user is the admin of the family
    """

    class Meta:
        db_table = "familyadmins"
    user_id = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), primary_key=True, unique=True,
                           null=False, blank=True)
    family_id = IntegerField(ForeignKey(Family, db_column='id', on_delete=CASCADE), null=False, blank=True)
    admin = BooleanField(null=False, blank=True)
