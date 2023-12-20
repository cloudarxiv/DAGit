#!/usr/bin/env python3
import os
import time
import json
import sys
import time

def main():
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    number = params["number"]
    if(number%2==0):
        result="even"
    else:
        result="odd"
    print(json.dumps({"activation_id": str(activation_id),
                        "number": number,
                        "result": result,
                        
                    }))
    return({ "activation_id": str(activation_id),
            "number": number,
            "result": result,
            })
    

    

if __name__ == "__main__":
    main()