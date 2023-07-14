import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout,QHBoxLayout, QWidget)
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt
from PIL import Image
# import cv2
import glob
import time
import os
import json

from racketpose.alphapose.demo_api import SingleImageAlphaPose
from alphapose.utils.config import update_config
from alphapose.utils.pPose_nms import write_json

from widgets import  ImageDisplay, ImageNavigator
from util import get_image_names, pose_detect,draw_pose,Settings,save_label, load_label


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        self.setWindowTitle('Image Browser')
        # self.setGeometry(100, 100, 1000, 800)

        # Creating the layout
        self.layout = QVBoxLayout()
        
        # Create a push button
        self.open_button = QPushButton('Open Browser')
        self.layout.addWidget(self.open_button)

        self.navigator = ImageNavigator()

        # Create a image display widget
        self.pose_classes = ['idle','serve','forehand GS','backhand GS', 'forehand Volley','backhand Volley','overhead smash']
        self.image_display = ImageDisplay(w=1024,h=819)
        self.image_display.register_classes(self.pose_classes)
        # self.image_display = ImageDisplay(w=512,h=420)
        # 

        # save button
        self.save_button = QPushButton('save labels')
        
        # Setting up the widget to hold the layout
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.register_slots()
           
        self.idx = 0
        
        
        settings = Settings()
        self.pose_detector = SingleImageAlphaPose(settings, settings.get_cfg())
        
    def register_slots(self):
        self.open_button.clicked.connect(self.open_image)
        self.save_button.clicked.connect(self.save_label)     
        self.navigator.prev_button.clicked.connect(self.go_prev)
        self.navigator.next_button.clicked.connect(self.go_next)
        
    def open_image(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Open data directory', './')
        if self.directory:
            self.open_button.setParent(None)
            self.image_names =  get_image_names(self.directory)

            # interface changes
            self.display_image_and_name()
            self.layout.addWidget(self.navigator)
            self.layout.addWidget(self.image_display)
            self.layout.addWidget(self.save_button)

    def go_prev(self):
        idx = self.idx -1
        self.idx = idx if idx >=0 else len(self.image_names)-1
        self.display_image_and_name()

    def go_next(self):
        idx  = self.idx + 1
        self.idx = idx if idx < len(self.image_names) else 0
        self.display_image_and_name()

    def display_image_and_name(self):
        img_name = self.image_names[self.idx]
        label_name = img_name[:-3] + 'json'
        image = Image.open(img_name)
        if not os.path.exists(label_name):
            pose = pose_detect(image,self.pose_detector)
            for rst in pose['result']:
                rst['pose_label'] = self.pose_classes[0]
            save_label(img_name,label_name,pose)
        else:
            pose = load_label(label_name)

        if self.idx >0:
            prev_image_name = self.image_names[self.idx-1]
            prev_label_name = prev_image_name[:-3] + 'json'
            prev_pose = load_label(prev_label_name)
            M = len(pose['result'])
            N = len(prev_pose['result'])
            for i in range(M):
                if i < N:
                    pose['result'][i]['pose_label'] = prev_pose['result'][i]['pose_label']
                    print('previous label',prev_pose['result'][i]['pose_label'])
                else:
                    pose['result'][i]['pose_label'] = self.pose_classes[0]
        save_label(img_name,label_name,pose)
        image =  draw_pose(image,pose)
        self.image_display.set_pose(pose)
        self.image_display.show_img(image)
        self.navigator.set_text_and_progress(img_name, 1 + self.idx, len(self.image_names))

    def save_label(self):
        print('saved')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
