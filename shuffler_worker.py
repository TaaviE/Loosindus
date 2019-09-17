# coding=utf-8
"""
Celery worker that solves the graph problem given to it
"""
from main import celery


@celery.task(bind=True)
def calculate_shuffle(self, people, connections):
    """
    Just calculates a shuffle based on the given parameters
    """

    return None
