import onnxruntime as ort
import cv2
import numpy as np

class NoGPUAvailable(Exception):
    pass

class Wrapper():
    def __init__(self, model_type="segmentation"):
        #Load the model
        self.model_type=model_type
        if model_type=="bezier":
            self.sess_ort = ort.InferenceSession("/code/exercise_ws/checkpoints/segmentation_bezier.onnx")
            self.width=320
            self.height=240
        elif model_type=="segmentation":
            #self.sess_ort = ort.InferenceSession("/code/exercise_ws/checkpoints/segmentation.2012-12-11.onnx")
            self.sess_ort = ort.InferenceSession("/code/exercise_ws/checkpoints/segmentation_real.onnx")
            self.width=160
            self.height=120
        else:
            raise ValueError(f"Unsuported model type for segmentation: {model_type}")
        
    def segment_cv2_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        np_img = img_rgb.reshape((1,*img_rgb.shape))
        res = self.sess_ort.run(output_names=["output:0"], input_feed={"input_rgb:0": np_img.astype(np.float32)})
        self.seg=res[0].astype(np.uint8).squeeze()
        if self.model_type=="segmentation": #Mapping is reversed between the two models
            self.yellow_lines_mask = (self.seg==1).astype(np.uint8)
            self.white_lines_mask = (self.seg==2).astype(np.uint8)
            self.right_bezier_mask = (self.seg==5).astype(np.uint8)
            self.duckie_mask =  (self.seg==3).astype(np.uint8)
        elif self.model_type=="bezier":
            self.white_lines_mask = (self.seg==1).astype(np.uint8) ###
            self.yellow_lines_mask = (self.seg==2).astype(np.uint8) ###
            self.right_bezier_mask = (self.seg==5).astype(np.uint8)

    def get_nearest_duckies_px(self):
        return self.get_line_segments_px(self.duckie_mask, min_area=96)
        
    def get_seg(self):
        return self.seg
    
    def get_yellow_segments_px(self):
        #return self.get_nearest_segments_px(self.yellow_lines_mask)
        return self.get_line_segments_px(self.yellow_lines_mask)
    
    def get_white_segments_px(self, nearest_only=True): 
        #For the white segments, we dont want to be distracted by detection beyond the nearest white line.
        if nearest_only:
            return self.get_nearest_segments_px(self.white_lines_mask)
        else:
            return self.get_line_segments_px(self.white_lines_mask)

    def get_right_bezier_px(self):
        #return self.get_nearest_segments_px(self.right_bezier_mask)
        if self.model_type=="bezier":
            return self.get_line_segments_px(self.right_bezier_mask)
        else:
            return [] #Empty list

    def get_nearest_segments_px(self,mask):
        flip_mask = cv2.flip(mask, 0)
        line = np.argmax(flip_mask[:],axis=0)
        points=[]
        for x,y in enumerate(line):
            if (y!=0):
                y=-y+self.height-1
                points.append([x,y])
        segments_px=[]
        i=0
        pt1=None
        pt2=None
        for point in points:
            if i==0:
                pt1 = point
                i=1
                continue
            if i==1:
                pt2 = point
                segment = (pt1, pt2)
                segments_px.append(segment)
                i=0
                continue
        return segments_px

    @staticmethod
    def get_line_segments_px(mask, min_area=0 ):
        contours,_ = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_SIMPLE)
        segments_px = []
        for cnt in contours:
            i=0
            pt1=None
            pt2=None
            area = cv2.contourArea(cnt)
            if area<min_area:
                continue 
            for point in cnt:
                if i==0:
                    pt1 = tuple(point[0])
                    i=1
                    continue
                if i==1:
                    pt2 = tuple(point[0])
                    segment = (pt1, pt2)
                    segments_px.append(segment)
                    i=0
                    continue
        return segments_px

    
    def predict(self, batch_or_image):
        # TODO Make your model predict here!

        # TODO The given batch_or_image parameter will be a numpy array (ie either a 224 x 224 x 3 image, or a
        # TODO batch_size x 224 x 224 x 3 batch of images)
        # TODO These images will be 224 x 224, but feel free to have any model, so long as it can handle these
        # TODO dimensions. You could resize the images before predicting, make your model dimension-agnostic somehow,
        # TODO etc.

        # TODO This method should return a tuple of three lists of numpy arrays. The first is the bounding boxes, the
        # TODO second is the corresponding labels, the third is the scores (the probabilities)
        #img=batch_or_image[0:120,0:160,:]
        #img = np.random.random_sample((1,120,160,3)) * 255
        #res = self.sess_ort.run(output_names=["output:0"], input_feed={"input_rgb:0": img.reshape((1,120,160,3)).astype(np.float32)})

        # See this pseudocode for inspiration
        boxes = []
        labels = []
        scores = []
        for img in batch_or_image:  # or simply pipe the whole batch to the model instead of using a loop!
            pass
            #box, label, score = self.model.predict(img) # TODO you probably need to send the image to a tensor, etc.
            #boxes.append(box)
            #labels.append(label)
            #scores.append(score)

        return boxes, labels, scores

class Model():    # TODO probably extend a TF or Pytorch class!
    def __init__(self):
        # TODO Instantiate your weights etc here!
        pass
    # TODO add your own functions if need be!
