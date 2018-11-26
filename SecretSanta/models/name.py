from django.db.models import Model, CharField


class Name(Model):
    class Meta:
        db_table = "names_genitive"

    name = CharField(max_length=255, primary_key=True, null=False, blank=True)
    genitive = CharField(max_length=255, null=False, blank=True)
