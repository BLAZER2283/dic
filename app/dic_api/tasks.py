from celery import shared_task

@shared_task
def process_dic_task(task_id, image_before, image_after, subset_size, step, max_iter, min_correlation):
    from .dic_bisnes_logik.help_methods import HelpMethods
    HelpMethods()._process_dic_task(
        str(task_id), image_before, image_after, 
        subset_size, step, max_iter, min_correlation
    )