import os
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image
import torch
import requests

def main(params):
    activation_id = os.environ.get('__OW_ACTIVATION_ID')
    modelpath = 'models/transformers'
    url = params["url"]
    # url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)

    model = YolosForObjectDetection.from_pretrained(modelpath)
    image_processor = YolosImageProcessor.from_pretrained(modelpath)

    inputs = image_processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # model predicts bounding boxes and corresponding COCO classes
    logits = outputs.logits
    bboxes = outputs.pred_boxes

    results = []
    # print results
    target_sizes = torch.tensor([image.size[::-1]])
    results = image_processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        # results.append()
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )
    return({"activation_id": str(activation_id),
            "message":"success"
        })
        
    

    

if __name__ == "__main__":
    main(params)
