import cv2
from colorama import Fore, init
import numpy as np

# Constants for colors
init()
BLU = (255, 0, 0)
GRN = (0, 255, 0)
RED = (0, 0, 255)

eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


class LURD():
    def __init__(self, l:int=None , u:int=None, r:int=None, d:int=None):
        self.left = l if l else 0 if l==0 else None
        self.up = u if u else 0 if u==0 else None
        self.right = r if r else 0 if r==0 else None
        self.down = d if d else 0 if d==0 else None

    def _verify(self):
        if self.left == None or self.up == None or self.right == None or self.down == None:
            return False
        return True
    
    def __str__(self):
        return f"({self.left}, {self.up}, {self.right}, {self.down})"

class SELECT():
    def __init__(self, index:int):
        self.index = index
        self.history = []
        self.start = (None, None)
        self.final = (None, None)
        self.rec = LURD()
        self.image = []
        self.image_eye_center = (0, 0)
        self.frame_eye_center = (0, 0)

    def _rectangle(self):
        p1 = self.start
        p2 = self.final
        if p1==(None, None) or p2==(None, None):
            return False
        if p1[0] == p2[0] or p1[1] == p2[1]:
            return False
        else:
            left = min(p1[0], p2[0])
            right = max(p1[0], p2[0])
            up = min(p1[1], p2[1])
            down= max(p1[1], p2[1])
            self.rec = LURD(left, up, right, down)
            return True

    def _detect_eyes(self):     # 根據select.image+模型找出眼睛的位置
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray)
        if len(eyes)+len(self.history)==0:
            pass
            return
        x, y, w, h, find = 0, 0, 0, 0, 0
        if len(eyes):
            x, y, w, h = eyes[0]
            self.history.append( (x, y, x+w, y+h) )                 # 相對於 image 的邊框位置
            find = 1
        else:
            left, up, right, down = self.history[-1]
            x, y, w, h = left, up, right-left, down-up
            find = 0
        if len(self.history)>=48:
            self.history.pop(0)
        cv2.rectangle(self.image, (x, y), (x+w, y+h), RED, 3)   # 在邊框位置畫紅色
        self.image_eye_center = (x+w//2,y+h//2)                             # image 裡眼睛的位置
        self.frame_eye_center = (self.rec.left+x+w//2, self.rec.up+y+h//2)  # 全畫中眼睛的位置
        return find

    def _move(self):
        if len(self.history):
            width, height, depth = self.image.shape             # image 的寬(左右)*高(上下)
            left, up, right, down = self.history[-1]            # 相對於 image 的邊框位置
            remain = LURD(left, up, width-right, height-down)   # image 內四個方向剩餘的空間
            dd = LURD(0, 0, 0, 0)
            dd.left  = 13-remain.left
            dd.right = 13-remain.right
            dd.up    = 13-remain.up
            dd.down  = 13-remain.down
            self.rec.left -= dd.left
            self.rec.up -= dd.up
            self.rec.right += dd.right
            self.rec.down += dd.down
        pass

def mouse_callback(event, x, y, flags, param:list[SELECT]):
    op = param[0]
    if event == cv2.EVENT_LBUTTONDOWN:  # 滑鼠按下
        param[0].start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:  # 滑鼠移動
        if flags & cv2.EVENT_FLAG_LBUTTON:  # 按住的情況下
            if x<0 or y<0 or x>=WIDTH or y>=HEIGHT: # 超過視窗介面的時候，不合法
                param[0] = SELECT(0)
                return
            length = min(abs(x-op.start[0]), abs(y-op.start[1]))
            fx = op.start[0] + (length if x>op.start[0] else (-length))
            fy = op.start[1] + (length if y>op.start[1] else (-length))
            param[0].final = (fx, fy)
            param[0]._rectangle()

    elif event == cv2.EVENT_LBUTTONUP:  # 滑鼠放開
        valid = param[0]._rectangle()
        if valid:
            if len(param)==3:           # 已經有 2 個綠色框框
                cv2.destroyWindow("rectangle-1")
                cv2.destroyWindow("rectangle-2")
                param.pop()
                param.pop()
            param[0].index = len(param)
            param.append( param[0] )
        param[0] = SELECT(0)

def mosaic(frame, grid=int):    # 整個畫面由 grid*grid 馬賽克區塊組成
    block_width = WIDTH // grid
    block_height = HEIGHT // grid
    result = np.zeros((grid, grid, 3), dtype=np.uint8)
    for i in range(grid):
        for j in range(grid):
            x_start = j * block_width
            x_end = min(WIDTH, (j + 1) * block_width)
            y_start = i * block_height
            y_end = min(HEIGHT, (i + 1) * block_height)

            block = frame[y_start:y_end, x_start:x_end]
            avg_color = block.mean(axis=(0, 1)).astype(np.uint8)
            result[i][j] = avg_color
    return result



def main():
    
    selects = [SELECT(0)]               # index-0是使用者互動，index-1,2才是真的綠色框框框住眼睛
    cv2.namedWindow("Mouse Interaction", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Mouse Interaction", mouse_callback, selects)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: cap.read()")
            break

        frame = cv2.flip(frame, 1)
        show = np.copy(frame)


        for index, select in enumerate(selects):
            if not select.rec._verify():                                                # 還不是一個成熟的 rec
                continue
            rec = select.rec                                                            # rec 是 LERD 物件
            left, up, right, down = rec.left, rec.up, rec.right, rec.down               # 相對於全畫面的上下左右
            cv2.rectangle(show, (left, up), (right, down), GRN if index else BLU, 2)    # 綠色是框好的，藍色是正在框的
            if not index:
                continue
            select.image = show[max(0,up+2):min(HEIGHT,down-2), max(0,left+2):min(WIDTH,right-2)]# 抓取frame中框住的畫面
            find = select._detect_eyes()                                                # 用roi+模型 盡可能抓出眼睛
            cv2.circle(show, select.frame_eye_center, 5, BLU, -1)                       # 在全畫中 點出藍色 眼睛的位置
            cv2.namedWindow(f"rectangle-{index}", cv2.WINDOW_NORMAL)
            cv2.imshow(f"rectangle-{index}", select.image)
            if find:
                select._move()

        cv2.imshow("Mouse Interaction", show)
        
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        if key == ord('r'):
            for x in range(1,len(selects)):
                cv2.destroyWindow(f"rectangle-{x}")
                selects.pop()
        


if __name__ == "__main__":
    main()