from app.celery_worker import celery
from task_1 import substructure_search


@celery.task
def substructure_search_task(molecules, substructure):
    result = substructure_search(molecules, substructure)
    return result
