# run_worker.py
import multiprocessing
import sys
import os

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    # Add project root to sys.path so 'api' package can be imported
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from rq import SimpleWorker, Queue
    from app.core.redis_conn import get_redis

    # Connect to Redis
    redis_conn = get_redis()

    # Queue(s) to listen to
    queues = [Queue("exports", connection=redis_conn)]

    print("Starting RQ worker for queue: exports ...")
    worker = SimpleWorker(queues)
    worker.work()
