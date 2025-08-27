from celery_app import celery_app

# Run worker: celery -A worker.celery_app worker --loglevel=info
# Run flower: celery -A worker.celery_app flower --port=5555

if __name__ == "__main__":
    celery_app.start()
