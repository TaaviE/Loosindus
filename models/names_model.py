# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Specifies how Estonian names are stored in the DB with cases
"""
from sqlalchemy import Column, VARCHAR

from main import db


class Name(db.Model):
    """
    Specifies how names are stored in the database for Estonian localization
    """
    __tablename__ = "names_cases"

    name: str = Column(VARCHAR(255), primary_key=True, nullable=False)
    genitive: str = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return f"<id {self.name}>"

    def __str__(self):
        return f"{{\"name\": \"{self.name}\", \"genitive\": \"{self.genitive}\"}}"
