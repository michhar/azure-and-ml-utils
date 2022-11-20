# ML Labeling-Related Scripts


| Script | Description | Necessary Installs |
|---|---|---|
| `calc_anchors_yolo_format.py` | Calculate anchor boxes for YOLO blocks | |
| `custom_labeling_classificaiton.py` | Interactive script to label images for classification | `matplotlib` |
| `pascalvoc_to_YOLO.py` | Converts Pascal VOC format (VOTT generated) to YOLO format.  For use with Darknet program on Linux machine.  The annotations for this script originated from using the VOTT labeling tool. | . |
| `via_coco_to_delimited_text.py` | onvert from the VGG Image Annotator's (VIA) COCO export format to a space-separated text format called COCO-converted. | . |
| `vott2.0_to_yolo.py` | Convert the annotations from using VoTT 2.0 labeling tool to YOLO text format for this project. Also, creates a test.txt and train.txt file with paths to test and train images. | . |
| `yolo_to_pascal_voc.py` | Convert labels from the VoTT YOLO format to VoTT Tensorflow Pascal VOC format so that we can run kmeans.py to discover anchor sizes. | . |

