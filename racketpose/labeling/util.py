import glob
import numpy as np
import torch
from PIL import Image,ImageDraw,ImageFont
import time 
import json

from racketpose.alphapose.demo_api import SingleImageAlphaPose
from alphapose.utils.config import update_config
from alphapose.utils.pPose_nms import write_json
        
class Settings:
    def __init__(self):
        self.cfg = '/home/qingyu/AlphaPose/configs/halpe_26/resnet/256x192_res50_lr1e-3_1x.yaml'
        self.checkpoint = '/home/qingyu/AlphaPose/pretrained_models/halpe26_fast_res50_256x192.pth'
        self.detector = 'yolo'
        self.inputimg = '/home/qingyu/RacketPose/data/from_bag_1/img_000017.jpg'
        self.save_imag = False
        self.vis = True
        self.showbox = False
        self.profile = False
        self.format = 'coco'
        self.min_box_area = 0
        self.eval = False
        self.gpus = "0"
        self.flip = False
        self.debug = False
        self.vis_fast = False
        self.pose_flow = False
        self.pose_track = False

        self.gpus = [int(self.gpus[0])] if torch.cuda.device_count() >= 1 else [-1]
        self.device = torch.device("cuda:" + str(self.gpus[0]) if self.gpus[0] >= 0 else "cpu")
        self.tracking = self.pose_track or self.pose_flow or self.detector=='tracker'

    def get_cfg(self):
        return update_config(self.cfg)
    

def get_image_names(dir,suffix='jpg'):
    img_names = glob.glob(dir + '/*.' + suffix)
    img_names.sort()
    return img_names




def pose_detect(img,demo):

    img = np.array(img)
    process_time = -time.time()
    pose = demo.process('place_holder', img)
    process_time += time.time()
    print('process time = ',process_time)

    return pose

def draw_human_keypoints(img,pose):

    # https://github.com/Fang-Haoshu/Halpe-FullBody
    # skipped some points at feet
    links = [(10,8), (8,6), (6,18),(18,5), (5,7), (7,9),
             (4,2),(2,0),(0,1),(1,3),(17,18),
             (18,19),
             (19,12),(12,14),(14,16),(16,21),
             (19,11),(11,13),(13,15),(15,20)]
    
    pts = []
    for two in links:
        for one in two:
            if one not in pts:
                pts.append(one)
    r_pts = [8,14,16]
    l_pts = [7,13,15]

    draw = ImageDraw.Draw(img)

    # draw keypoints
    point_size = 2
    for rst in pose['result']:
        uvs = rst['keypoints']
        for pt in pts:
            x, y = uvs[pt]
            draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size), fill="red")

        # Link the points
        for s,e in links:
            if (s in r_pts) or (e in r_pts):
                color= 'green'
            elif (s in l_pts) or (e in l_pts):
                color = 'orange'
            else:
                color = 'blue'
            draw.line([tuple(uvs[s]), tuple(uvs[e])], fill=color, width=4)
        
        # label
        cx,cy,cw,ch = rst['bbox']
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf", 30)
        draw.text((cx+cw//3,cy+ch), rst['pose_label'], font = font, fill='yellow')
    return img

def draw_pose(img,pose):
    img = np.array(img)
    # img = detector.vis(img, pose)   # visulize the pose result
    # bbox
    for rst in pose['result']:
        cx,cy,cw,ch = rst['bbox']
        cx = int(cx);cy=int(cy);cw = int(cw); ch = int(ch)
        img[cy:cy+ch,cx:cx+cw,:] = img[cy:cy+ch,cx:cx+cw,:]  + 40
    img = np.clip(img,0,255).astype(np.uint8)
    img =Image.fromarray(img)

    img = draw_human_keypoints(img, pose)

    return img

def save_label(img_name,label_name,pose):
    save_pose = dict()
    save_pose['img_name'] = img_name 
    # save_pose['pose_label'] = pose['pose_label']
    save_pose['result'] = []
    for rst in pose['result']:
        itm = dict()
        for k,v in rst.items():
            if torch.is_tensor(v):
                itm[k] = v.tolist()
            else:
                itm[k] =v
        save_pose['result'].append(itm)
    with open(label_name, "w") as file:
        json.dump(save_pose, file)


def load_label(label_name):
    with open(label_name, "r") as file:
        pose = json.load(file)
    
    # tensor_set = ('keypoints','kp_score','proposal_score')
    # for rst in pose['result']:
    #     for k,v in rst.items():
    #         if k in tensor_set:
    #             rst[k] = torch.tensor(v)
            
    return pose

def check_inside(uv,bbox):
    u,v = uv
    x,y,w,h = bbox
    return True if (x<u<x+w) and (y<v<y+h) else False
