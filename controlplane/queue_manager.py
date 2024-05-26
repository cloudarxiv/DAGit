# queue_manager.py


# to implement multi-priority queue 
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
    
    

# if __name__ == "__main__":
#     qm = QueueManager('test_queue')
#     qm.enqueue('test_item')
#     qm.enqueue('test_item1')

#     qm.enqueue('test_item2')

    
#     print(f"Queue size after enqueue: {qm.size()}")
#     item = qm.dequeue()
#     print(f"Dequeued item: {item.decode('utf-8')}")
#     print(f"Queue size after dequeue: {qm.size()}")
