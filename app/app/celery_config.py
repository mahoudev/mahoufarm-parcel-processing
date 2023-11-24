from celery import Celery

celery_app = Celery("worker", backend="redis://localhost:6379/0", broker="redis://localhost:6379/0", broker_connection_retry_on_startup = True, include=['app.worker'])
# celery = celery_app

# celery_app.conf.task_routes = {
#     "app.worker.test_celery": "main-queue",
#     "app.worker.heavy_task": "main-queue",
#     "app.worker.notify_user": "main-queue",
#     "app.worker.check_task": "main-queue",

#     "app.worker.ai_parse_prescription": "main-queue",
#     "app.worker.check_state_ai_parsed_prescription": "main-queue",
#     "app.worker.notify_user_when_ai_parsed_prescription": "main-queue",
#     "app.worker.run_ai_parse_prescription": "main-queue",

# }

