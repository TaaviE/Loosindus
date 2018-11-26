from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, CASCADE, IntegerField, DateField


class Shuffle(Model):
    class Meta:
        db_table = "shuffles"

    giver = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), primary_key=True, null=False, blank=True)
    getter = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), null=False, blank=True)
    year = DateField(auto_now=True, null=False, blank=True)
