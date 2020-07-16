import onnxmltools
from keras.layers import Input

from yolo3.model import tiny_yolo_body
import argparse


def arg_parse():
    """Parse arguements to the detect module"""
    parser = argparse.ArgumentParser(description='YOLO v3 Video Detection Module')
   
    parser.add_argument("--model", dest='model', help = 
                        "Keras model to convert", type = str)

    return parser.parse_args()

args = arg_parse()


yolo_model = tiny_yolo_body(Input(shape=(416, 416, 3)), 6, 2)         
yolo_model.load_weights(args.model) # make sure model, anchors and classes match

# # Convert it! The target_opset parameter is optional.
# onnx_model = onnxmltools.convert_keras(keras_model, target_opset=7) 
