import redis

def create_redis_master_instance():   
    try:  
       
        r = redis.Redis(host="10.100.77.154", port=6379, db=2)
        print("Role:",r.info()['role'])
        return r
    except Exception as e:
        print("Error-",e)
        

def create_redis_slave_instance():  
    try:   
        r = redis.Redis(host="10.110.12.209", port=6379, db=2)
        print("Role:",r.info()['role'])
        return r
    except Exception as e:
        print("Error-",e)
