import copy, time, requests
from share import PERSON, ROOM
import cv2
import atexit
import threading

class PARAM():
    def __init__(self , pos:tuple[int, int]=(0, 0)):
        self.pos = pos

def mouse_callback(event, x, y, flags, param:PARAM):
    if event == cv2.EVENT_LBUTTONDOWN:  # 滑鼠按下
        pass
    elif event == cv2.EVENT_MOUSEMOVE:  # 滑鼠移動
        if flags & cv2.EVENT_FLAG_LBUTTON:  # 按住的情況下
            param.pos = (x, y)
            pass
    elif event == cv2.EVENT_LBUTTONUP:  # 滑鼠放開
        pass

def on_exit(url:str, user:PERSON):
    response = requests.post(f"{url}/bye" , json=user.to_dict())
    if response.status_code == 200:
        obj = PERSON.to_obj(response.json())
        print(obj.name)

def enroll(url:str, width:int=400, height:int=400)->PERSON:
    try:
        user = PERSON(WH=(width, height)) 
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

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # port = int(input("Enter the server port number: "))
    url = f"http://127.0.0.1:6000"

    myself = enroll(url, WIDTH, HEIGHT)
    room = ROOM()
    while True:
        c = input("action")
        if c=="c":
            room, myself = create(url, myself, room)
            print(f"in client")
            print(f"myself = {myself}")
            print(f"room = {room}")
        elif c=="i":
            room, myself = invite(url, myself, room)
            print(f"in client")
            print(f"myself = {myself}")
            print(f"room = {room}")
        elif c=="s":
            room, myself = search(url, myself, room)
            print(f"in client")
            print(f"myself = {myself}")
            print(f"room = {room}")
        elif c=="q":
            break


    # param = PARAM()
    # cv2.namedWindow("Mouse Interaction", cv2.WINDOW_NORMAL)
    # cv2.setMouseCallback("Mouse Interaction", mouse_callback, param)



if __name__ == "__main__":
    main()
