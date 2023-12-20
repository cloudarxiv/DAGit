#!/usr/bin/env python3

import os
import json
import sys
def main():
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    number = params["number"]
    flag=0
    for i in range(2,number//2):
        if(number%i==0):
            flag=1
            break
    if(flag==0):
        result="The number is prime"
    else:
        result = "The number is not prime"
    print(json.dumps({ "activation_id": str(activation_id),
                        "number": number,
                        "result": result,
                    }))

    return({ "activation_id": str(activation_id),
            "number": number,
            "result": result,
            })
    
    

if __name__ == "__main__":
    main()