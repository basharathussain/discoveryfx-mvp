"""RQ worker entry. Phase 1 keeps it idle — Phase 2 adds scrape jobs."""
import logging

from redis import Redis
from rq import Queue, Worker

from api.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("worker")


def main() -> None:
    redis_url = settings.redis_url.replace("redis://", "redis://")
    conn = Redis.from_url(redis_url)
    q = Queue("default", connection=conn)
    log.info("Worker started, queue=%s", q.name)
    Worker([q], connection=conn).work()


if __name__ == "__main__":
    main()
