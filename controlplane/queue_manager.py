# queue_manager.py
import redis

class QueueManager:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def enqueue(self, item):
        self.redis.rpush(self.queue_name, item)
    
    def dequeue(self):
        return self.redis.lpop(self.queue_name)
    
    def size(self):
        return self.redis.llen(self.queue_name)
    
    def flush(self):
        self.redis.flushdb()
    
