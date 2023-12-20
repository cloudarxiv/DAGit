#!/usr/bin/env python3
import os
import time
import json
import sys
import time
import logging



def main():
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    number = params["number"]
    # result1 = params["result"]
    print(json.dumps({ "activation_id": str(activation_id),
                        "number": number,
                        "result": "The number is odd",
                    }))

    return({ "activation_id": str(activation_id),
            "number": number,
            "result": "The number is odd",
            })
    
if __name__ == "__main__":
    main()