import copy, time, requests
from share import PERSON, DATA, ROOM
from typing import List
import cv2
import numpy as np
import queue
import atexit
import threading

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit(-1)
def mouse_callback(event, x, y, flags, data:DATA):
    if event == cv2.EVENT_MOUSEMOVE:  # 滑鼠移動
        if flags & cv2.EVENT_FLAG_LBUTTON:  # 按住的情況下
            if x<0 or x>data.WH[0] or y<0 or y>data.WH[1]:
                return
            data.point = (x, y)

def on_exit(url:str, user:PERSON):
    response = requests.post(f"{url}/bye" , json=user.to_dict())
    if response.status_code == 200:
        obj = PERSON.to_obj(response.json())
        print(obj.name)

def enroll(url:str)->PERSON:
    try:
        user = PERSON() 
        while True:
            user.name = input("Enter Your name: ").strip()
            if len(user.name) > 0:
                break
            print("Name cannot be empty. Please try again.")
        response = requests.post(f"{url}/enroll", json=user.to_dict())
        if response.status_code == 200:
            obj = PERSON.to_obj(response.json())
            atexit.register(on_exit, url, obj)
            return obj
        else:
            print("Error:", response.json())
            exit(0)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

def create(url:str, myself:PERSON, myroom:ROOM)->tuple[ROOM, PERSON]:
    try:
        again = True
        while again:
            while True:
                room = int(input("Create the rooom ID (0<=R<=3): "))
                if 0<=room and room<=3:
                    break
                print("0<= roomID <=3: ")
            response = requests.post(f"{url}/create/{room}", json=myself.to_dict())
            if response.status_code == 200:
                response = response.json()
                user = PERSON.to_obj(response["user"])
                room = ROOM.to_obj(response["room"])
                print(f"Yor are a creator {user}")
                print(f"create successfully: {room}")
                return room, user
            else:
                print("Error:", response.json())
                again = True if input("Again? [ Y / N ] : ")=="Y" else False
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    return myroom, myself

def invite(url:str, myself:PERSON, myroom:ROOM)->tuple[ROOM, PERSON]:
    try:
        again = True
        while again:
            while True:
                name = input("Enter the name You want to invite: ")
                if len(name) > 0:
                    break
                print("Name cannot be empty. Please try again. ")
            response = requests.post(f"{url}/invite/{name}", json=myself.to_dict())
            if response.status_code == 200:
                response = response.json()
                user = PERSON.to_obj(response["user"])
                room = ROOM.to_obj(response["room"])
                print(f"Yor are a inviter {user}")
                print(f"invite successfully: {room}")
                return room, user
            print("Error:", response.json())
            again = True if input("Again? [ Y / N ] : ")=="Y" else False
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)    
    return myroom, myself

def search(url:str, myself:PERSON, myroom:ROOM)->tuple[ROOM, PERSON]:
    try:
        again = True
        while again:
            while True:
                room = int(input("Search the rooom ID (0<=R<=3): "))
                if 0<=room and room<=3:
                    break
                print("0<= roomID <=3.")
            response = requests.post(f"{url}/search/{room}", json=myself.to_dict())
            if response.status_code == 200:
                response = response.json()
                user = PERSON.to_obj(response["user"])
                room = ROOM.to_obj(response["room"])
                print(f"Yor are a searcher {user}")
                print(f"search successfully: {room}")
                return room, user
            print("Error:", response.json())
            again = True if input("Again? [ Y / N ] : ")=="Y" else False
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    return myroom, myself

def watch(url:str, mydata:DATA)->None:
    global cap
    WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    mydata.WH = (WIDTH, HEIGHT)
    try:
        data = None
        while True:
            time.sleep(0.03)
            ret, frame = cap.read()
            if not ret:
                print("Error: cap.read()")
                exit(-1)
            mydata.mosaic = to_mosaic(frame, grid=16, WIDTH=WIDTH, HEIGHT=HEIGHT)               # 全畫面 馬賽克
            if data is not None:
                mydata.detail , mydata.seen = part_frame(frame, data.point, 0.1)               # 對於 point 附近做細節
            else:
                mydata.detail , mydata.seen = part_frame(frame, (WIDTH//2, HEIGHT//2), 0.1)     # 對於 point 附近做 detail
            response = requests.post(f"{url}/watch/{mydata.ID}", json=mydata.to_dict())
            if response.status_code == 200:
                data = DATA.to_obj(response.json())
                if data.valid:
                    if not cv2.getWindowProperty(data.name, cv2.WND_PROP_VISIBLE):
                        cv2.destroyAllWindows()
                        cv2.namedWindow(data.name, cv2.WINDOW_NORMAL)
                        cv2.setMouseCallback(data.name, mouse_callback, mydata)                   # 其他人的data
                    if data.mosaic.dtype != "uint8":                
                        data.mosaic = cv2.normalize(data.mosaic, None, 0, 255, cv2.NORM_MINMAX) # type 要符合cv2
                        data.mosaic = data.mosaic.astype("uint8")                               # type 要符合cv2
                    ciasom = to_ciasom(data.mosaic, data.grid, data.WH[0], data.WH[1])          # 將馬賽克放大到對方原本的大小
                    result = merge(ciasom, data.detail, data.WH, data.seen)                     # 將 detail 和 放大的馬賽克結合
                    cv2.imshow(data.name, result)                                               # 展示 result
                    window_ratio(data.name, WIDTH, HEIGHT)                                      # 讓畫面保持比例
                    if cv2.waitKey(1) & 0xff == ord("q"):
                        cv2.destroyWindow(data.name)
                        print(f"close {data.name} window")
                        exit(0)
            else:
                print("Error:", response.json())
                break
        return None
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

def window_ratio(window_name:str, WIDTH:int, HEIGHT:int):
    cv2.waitKey(1)
    window_size = cv2.getWindowImageRect(window_name)
    if window_size:
        _, _, current_width, current_height = window_size
        aspect_ratio = WIDTH / HEIGHT
        if current_width / current_height > aspect_ratio:
            new_width = int(current_height * aspect_ratio)
            new_height = current_height
        else:
            new_width = current_width
            new_height = int(current_width / aspect_ratio)
        cv2.resizeWindow(window_name, new_width, new_height)

def part_frame(frame, point:tuple[int, int], side_ratio=0.1)->tuple[np.ndarray, tuple[tuple[int, int], tuple[int, int]]]:
    frame_height, frame_width, channels = frame.shape
    half_width = int(frame_width*side_ratio)
    half_height = int(frame_height*side_ratio)

    x1 = max(0, point[0] - half_width)
    y1 = max(0, point[1] - half_height)
    x2 = min(frame_width, point[0] + half_width)
    y2 = min(frame_height, point[1] + half_height)

    preserved_region = frame[y1:y2, x1:x2].copy()
    return preserved_region, ((x1, y1), (x2, y2))

def to_mosaic(frame, grid:int, WIDTH:int, HEIGHT:int):
    compressed_height = HEIGHT // grid
    compressed_width = WIDTH // grid
    result = np.zeros((compressed_height, compressed_width, 3), dtype=np.uint8)
    for i in range(compressed_height):
        for j in range(compressed_width):
            y_start = max(i*grid, 0)
            y_end   = min((i+1)*grid, HEIGHT)
            x_start = max(j*grid, 0)
            x_end   = min((j+1)*grid, WIDTH)
            block = frame[y_start:y_end, x_start:x_end]
            avg_color = block.mean(axis=(0, 1)).astype(np.uint8)
            result[i, j] = avg_color
    return result

def to_ciasom(mosaic, grid:int, large_width:int, large_height:int):
    # mosaic_height, mosaic_width, _ = mosaic.shape
    # result = np.zeros((large_height, large_width, 3), dtype=np.uint8)
    # for i in range(mosaic_height):
    #     for j in range(mosaic_width):
    #         avg_color = mosaic[i, j]
    #         y_start = i * grid
    #         y_end = min((i + 1) * grid, large_height)
    #         x_start = j * grid
    #         x_end = min((j + 1) * grid, large_width)
    #         result[y_start:y_end, x_start:x_end] = avg_color
    mosaic_height, mosaic_width, _ = mosaic.shape
    expanded = np.repeat(np.repeat(mosaic, grid, axis=0), grid, axis=1)
    result = expanded[:large_height, :large_width]
    return result

def merge(mosaic, detail, WH:tuple[int, int], seen:tuple[tuple[int, int], tuple[int, int]]):
    mosaic_height, mosaic_width, mosaic_channels = mosaic.shape
    detail_height, detail_width, detail_channels = detail.shape
    x1, y1 = seen[0]
    x2, y2 = seen[1]
    if mosaic_width != WH[0] or mosaic_height != WH[1]:
        return mosaic
    if mosaic_channels != detail_channels:
        return mosaic
    if (x2-x1) != detail_width or (y2-y1) != detail_height:
        return mosaic
    merged_image = mosaic.copy()
    merged_image[y1:y2, x1:x2] = detail
    return merged_image


def main():
    # cap = cv2.VideoCapture(0)
    # if not cap.isOpened():
    #     print("Error: Could not open webcam.")
    #     exit()
    # WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # port = int(input("Enter the server port number: "))
    url = f"http://140.112.30.168:6000"

    myself = enroll(url)
    myroom = ROOM()
    mydata = DATA(ID=myself.ID, name=myself.name, grid=16, valid=True)
    while True:
        # print(f"{myself}")
        # print(f"{myroom}")
        c = input("action[ create/ invite/ search/ ok/ exit]: ")
        if c=="create" or c=="c":
            myroom, myself = create(url, myself, myroom)
        elif c=="invite" or c=="i":
            myroom, myself = invite(url, myself, myroom)
        elif c=="search" or c=="s":
            myroom, myself = search(url, myself, myroom)
        elif c=="ok" or c=="o":
            break
        elif c=="exit" or c=="e":
            return
    
    while True:
        # ret, frame = cap.read()
        # if not ret:
        #     print("Error: cap.read()")
        #     break
        # mydata.mosaic = to_mosaic(frame, grid=16, WIDTH=WIDTH, HEIGHT=HEIGHT)
        watch(url, mydata)
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break

        

if __name__ == "__main__":
    main()
