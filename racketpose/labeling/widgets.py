
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QLabel,QHBoxLayout, QVBoxLayout, QWidget,QSizePolicy,QShortcut,
                             QMenu,QAction)
from PyQt5.QtGui import QPixmap, QIcon, QImage,QKeySequence,QCursor
from PyQt5.QtCore import Qt, QPoint,QSize
from PIL import Image
from functools import partial
from util import get_image_names, pose_detect,draw_pose,Settings,save_label, load_label, check_inside

# import cv2
"""
widgets for the app, without slots
"""

class ImageNavigator(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        self.prev_button = QPushButton('<')
        self.layout.addWidget(self.prev_button)
        self.prev_button.resize(20,20)

        self.image_name = QLabel()
        self.layout.addWidget(self.image_name)
        

        self.next_button = QPushButton('>')
        self.next_button.resize(20,20)
        self.layout.addWidget(self.next_button)

        self.layout.setContentsMargins(150, 0, 150, 0)  # (self, left: int, top: int, right: int, bottom: int)
        self.layout.setSpacing(150)  # Set spacing between widgets to 20 pixels
        self.set_shortcuts()
        
    def set_shortcuts(self):
        shortcut = QShortcut(QKeySequence("d"), self)  # Create shortcut for "a" key
        shortcut.activated.connect(self.next_button.click)  # Connect the shortcut to the button's click event
        shortcut = QShortcut(QKeySequence("a"), self)  # Create shortcut for "d" key
        shortcut.activated.connect(self.prev_button.click)  # Connect the shortcut to the button's click event

    def set_text_and_progress(self,text, curr, tot):
        self.image_name.setText(text + f' ({curr}/{tot})')


class ImageDisplay(QWidget):
    def __init__(self,w=640,h=512):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_image = QLabel(self)
        self.lbl_image.setStyleSheet("padding :0px;background-color: red;")
        self.lbl_image.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.lbl_image,alignment=Qt.AlignLeft)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.lbl_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.widget_w = w
        self.widget_h = h

    def register_classes(self,pose):
        self.pose_classes =  pose

    def show_context_menu(self, pos):
        
        padding_x = (self.widget_w - self.image_w)//2
        padding_y = (self.widget_h - self.image_h)//2

        pos_x = pos.x()
        pos_y = pos.y()

        pos_u = (pos_x - padding_x)/self.image_scale
        pos_v = (pos_y - padding_y)/self.image_scale

        print(pos_u,pos_v)

        click_pose_id = None
        for id,rst in enumerate(self.pose['result']):
            if check_inside((pos_u,pos_v),rst['bbox']):
                click_pose_id = id

        if click_pose_id is not None:
            print('show menu')
            menu = QMenu()
            for pose_class in self.pose_classes:
                action = QAction(pose_class, menu)
                action.triggered.connect(partial(self.menu_action_callback, pose_class,click_pose_id))
                menu.addAction(action)
            menu.exec_(self.mapToGlobal(pos))


    def get_resize_dim(self):
        rh = self.widget_h / self.image_h_act 
        rw =  self.widget_w / self.image_w_act
        r = rh if rh < rw else rw
        self.image_w = int(r * self.image_w_act)
        self.image_h = int(r * self.image_h_act )
        self.image_scale = r

    def menu_action_callback(self,pose_class,click_pose_id):

        self.pose['result'][click_pose_id]['pose_label'] = pose_class
        img_name = self.pose['img_name']
        label_name = img_name[:-3] + 'json'
        save_label(self.pose['img_name'],label_name,self.pose)
        image = Image.open(img_name)
        image =  draw_pose(image,self.pose)
        self.show_img(image)



    def set_pose(self,pose):
        self.pose = pose

    def show_img(self, image):
        w, h = image.size
        self.image_w_act = w
        self.image_h_act = h
        self.get_resize_dim()
        # resized = cv2.resize(image, size, interpolation = cv2.INTER_AREA)
        image = image.resize((self.image_w,self.image_h)) 
        image = image.convert('RGBA')
        # Convert PIL image object to QImage object
        # qim = QImage(image.data, size[0], size[1], QImage.Format_RGB888).rgbSwapped()
        qim = QImage(image.tobytes('raw', 'RGBA'), self.image_w, self.image_h , QImage.Format_RGBA8888)
        # Create QPixmap from QImage
        pixmap = QPixmap.fromImage(qim)
        # Showing image in the label
        self.lbl_image.setPixmap(pixmap)
        self.lbl_image.setAlignment(Qt.AlignCenter)
        