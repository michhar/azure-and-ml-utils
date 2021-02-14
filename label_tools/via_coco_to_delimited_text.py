"""
Convert from the VGG Image Annotator's (VIA) COCO export format
to a space-separated text format called COCO-converted.

VIA tool:  http://www.robots.ox.ac.uk/~vgg/software/via/

Project with which this was created: https://github.com/hhk7734/tensorflow-yolov4
Link to original script:  https://wiki.loliot.net/docs/lang/python/libraries/yolov4/python-yolov4-dataset
Original script author:  Hyeonki Hong
Modified by:  Micheleen Harris

From VIA COCO format in json (where bbox is [xmin, ymin, width, height]):

{
    "info":{
       "year":2021,
       "version":"1",
       "description":"Exported using VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via/)",
       "contributor":"",
       "url":"http://www.robots.ox.ac.uk/~vgg/software/via/",
       "date_created":"Thu Feb 11 2021 16:01:55 GMT-0800 (PST)"
    },
    "images":[
       {
          "id":0,
          "width":1920,
          "height":1080,
          "file_name":"image1.jpg",
          "license":1,
          "date_captured":""
       },
       {
          "id":1,
          "width":1920,
          "height":1080,
          "file_name":"image2.jpg",
          "license":1,
          "date_captured":""
       }
    ],
    "annotations":[
       {
          "id":0,
          "image_id":"1",
          "category_id":1,
          "segmentation":[ ... ],
          "area":8484,
          "bbox":[ 1598, 415, 84, 101 ],
          "iscrowd":0
       },
       {
          "id":2,
          "image_id":"1",
          "category_id":1,
          "segmentation":[ ... ],
          "area":8400,
          "bbox":[ 1598, 415, 84, 100 ],
          "iscrowd":0
       },
       {
          "id":3,
          "image_id":"2",
          "category_id":2,
          "segmentation":[ ... ],
          "area":10815,
          "bbox":[ 1172, 328, 103, 105 ],
          "iscrowd":0
       }
    ],
    "licenses":[
       {
          "id":1,
          "name":"Unknown",
          "url":""
       }
    ],
    "categories":[
       {
          "id":1,
          "name":"no_hardhat",
          "supercategory":"label"
       },
       {
          "id":2,
          "name":"hardhat",
          "supercategory":"label"
       }
    ]
 }

To a delimited text format ("coco-converted") (where bounding box is [x-center,y-center,width,height]):

image1.jpg 1,<center_x>,<center_y>,<width>,<height> 1,<center_x>,<center_y>,<width>,<height>
image2.jpg 2,<center_x>,<center_y>,<width>,<height>
...

"""
import json
from collections import OrderedDict
from tqdm import tqdm
import argparse


def read_annots(coco_json, coco_names_path):
    """
    Read annotations from VIA exported coco json
    format and creates data dicts and names output
    file.

    Parameters
    ----------
    coco_json : str
        COCO json input file
    coco_names_path : str
        Names or labels output file

    Returns
    -------
    images : dict
        images dictionary
    annotations : dict
        annotations dictionary
    categories : dict
        categories or labels dictionary
    """
    coco = json.load(open(coco_json))
    images = coco["images"]
    annotations = coco["annotations"]
    categories = coco["categories"]

    class_to_id = {}
    # id_to_class = {}

    with open(coco_names_path, 'w') as fp:
        idx = 0
        for cat in categories:
            id = cat["name"].strip()
            class_name = cat["name"].strip()
            fp.write(class_name+"\n")

            # id_to_class[idx] = class_name
            class_to_id[class_name] = idx

    print("size of images {}".format(len(images)))
    print("size of annotations {}".format(len(annotations)))
    print("size of categories {}".format(len(categories)))

    return images, annotations, categories, class_to_id

def convert(images, annotations, categories, class_to_id):
    """Convert bounding boxes and output the dataset indexed
    by image id for creating an output file easily.

    Parameters
    ----------
    images : dict
        Images dictionary
    annotations : dict
        Annotations dictionary
    categories : dict
        Categories or labels dictionary
    class_to_id : dict
        Labels/classes to an index value

    Returns
    -------
    dataset : OrderedDict
        Annotations converted indexed by image id
    """
    dataset = {}

    for annotation in tqdm(annotations, desc="Parsing"):
        image_id = annotation["image_id"]
        category_id = annotation["category_id"]

        # Find image
        file_name = None
        image_height = 0
        image_width = 0
        for image in images:
            if int(image["id"]) == int(image_id):
                file_name = image["file_name"]
                image_height = image["height"]
                image_width = image["width"]
                break

        if file_name is None:
            continue

        # Find class id
        class_id = None
        for category in categories:
            if category["id"] == category_id:
                category_name = category["name"]
                class_id = class_to_id.get(category_name)
                break

        if class_id is None:
            continue

        # Calculate x,y,w,h
        x_center = annotation["bbox"][0] + annotation["bbox"][2] / 2
        x_center /= image_width
        y_center = annotation["bbox"][1] + annotation["bbox"][3] / 2
        y_center /= image_height
        width = annotation["bbox"][2] / image_width
        height = annotation["bbox"][3] / image_height

        if dataset.get(image_id):
            dataset[image_id][1].append(
                [class_id, x_center, y_center, width, height]
            )
        else:
            dataset[image_id] = [
                file_name,
                [[class_id, x_center, y_center, width, height]],
            ]

    dataset = OrderedDict(sorted(dataset.items()))
    return dataset

def write_output(dataset, out_file_path):
    """Write output file based on converted annotations
    
    Parameters
    ----------
    dataset : OrdereDict
        Annotations converted indexed by image id
    out_file_path : str
        Final output annotatinos file path

    Returns
    -------
    None
    """
    with open(out_file_path, "w") as fd:
        for image_id, bboxes in tqdm(dataset.items(), desc="Saving"):
            data = bboxes[0]
            for bbox in bboxes[1]:
                data += " "
                data += "{:d},".format(bbox[0])
                data += "{:8.6f},".format(bbox[1])
                data += "{:8.6f},".format(bbox[2])
                data += "{:8.6f},".format(bbox[3])
                data += "{:8.6f}".format(bbox[4])

            data += "\n"
            fd.write(data)

if __name__ == "__main__":
    """Main"""

    # For command line options
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        '--cocojson-path', type=str, dest='coco_json',
        help='Annotations from VIA COCO format export, e.g. "via_export_coco.json"'
    )

    parser.add_argument(
        '--out-path', type=str, dest='out_file', default='converted-coco.txt',
        help='Output converted-coco file - caution, will overwrite!'
    )

    parser.add_argument(
        '--out-names-path', type=str, dest='out_names_file', default='custom.names',
        help='Output "names" or labels file - caution, will overwrite!'
    )

    args = parser.parse_args()

    images, annotations, categories, class_to_id = read_annots(args.coco_json, args.out_names_file)
    dataset = convert(images, annotations, categories, class_to_id)
    write_output(dataset, args.out_file)

