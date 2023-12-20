#!/usr/bin/env python3

import os
import json
import sys
def main():
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    params = json.loads(sys.argv[1])
    number = params["number"]
    print(json.dumps({ "activation_id": str(activation_id),
                        "number": number,
                        "result": "The number is even",
                    }))

    return({ "activation_id": str(activation_id),
            "number": number,
            "result": "The number is even",
            })
    
    

if __name__ == "__main__":
    main()