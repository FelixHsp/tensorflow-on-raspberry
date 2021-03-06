import numpy as np
import os
import sys
import tarfile
import tensorflow as tf
import cv2
import time

from collections import defaultdict

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("../..")

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# What model to download.
MODEL_NAME = 'ggpp'
#MODEL_NAME = 'faster_rcnn_resnet101_coco_11_06_2017'
#MODEL_NAME = 'ssd_inception_v2_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('/home/pi/tf/models-master/research/object_detection/data', 'ggpp.pbtxt')

#extract the ssd_mobilenet
start = time.clock()
NUM_CLASSES = 90
#opener = urllib.request.URLopener()
#opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
tar_file = tarfile.open(MODEL_FILE)
for file in tar_file.getmembers():
   file_name = os.path.basename(file.name)
   if 'frozen_inference_graph.pb' in file_name:
      tar_file.extract(file, os.getcwd())
end= time.clock()
print('load the model',(end-start))
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)

categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

cap = cv2.VideoCapture(0)
with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
      writer = tf.summary.FileWriter("logs/", sess.graph)
      sess.run(tf.global_variables_initializer())
      while(1):
        start = time.clock()
        ret, frame = cap.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        image_np=frame
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = detection_graph.get_tensor_by_name('detection_scores:0')
        classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        # Actual detection.

        (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          line_thickness=6)
        end = time.clock()
        #print('frame:',1.0/(end - start))
        print ('One frame detect take time:'),end - start

        cv2.imshow("Felix", image_np)
        print('after cv2 show')
        cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()