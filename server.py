from flask import Flask, request, jsonify
from share import PERSON, DATA, ROOM
import threading, time
import copy
import numpy as np

app = Flask(__name__)
clients = [PERSON(ID=index) for index in range(8)]
rooms = [ROOM(RID=index,ID=[], data=[], present=[]) for index in range(4)]

fake = DATA(ID=-1,
            name="fake",
            index=-1,
            grid=16,
            WH=(640,480),
            point=(320,240),
            mosaic=np.array([
                [[255, 0, 0], [0, 255, 0], [0, 0, 255]],  # Red, Green, Blue
                [[255, 255, 0], [0, 255, 255], [255, 0, 255]],  # Yellow, Cyan, Magenta
                [[192, 192, 192], [128, 128, 128], [64, 64, 64]]  # Light gray, gray, dark gray
            ], dtype=np.uint8),
            valid=True)

def S10():
    for index, client in enumerate(clients):
        if client.valid:
            print(f"clients[{index}] = {client}")
    for index, room in enumerate(rooms):
        if len(room.ID):
            print(f"rooms[{index}] = {room}")
    threading.Timer(3, S10).start()

@app.route("/bye", methods=["POST"])
def bye():
    global clients, rooms
    user = PERSON.to_obj(request.json)
    if user.ID<0 or user.ID>=8:
        return jsonify({"message": f"Invalid ID {user.ID}"}), 400
    print(f"clients[{user.ID}] clear")
    if user.room:
        room = rooms[user.room]     # 如果正在視訊 是否 需要斷開連結
        # room.data.pop(user.index)
        # room.present.pop(user.index)
        # room.ID.pop(user.index)
    clients[user.ID] = PERSON(ID=user.ID)
    user.name = "bye"
    return jsonify(user.to_dict()), 200

@app.route("/enroll", methods=["POST"])
def enroll():
    global clients, rooms
    user = PERSON.to_obj(request.json)
    for index, client in enumerate(clients):
        if not user.valid and not client.valid: # 還沒找到 and 這格沒有使用者佔走
            user.ID = index
            user.valid = True
        if client.name == user.name:            # handle once find repeat name
            return jsonify({"message": "The name has existed already."}), 400
    if not user.valid:                          # no repeat name = no available quota
        return jsonify({"message": "There is no available space for clients."}), 503
    clients[user.ID] = user                     # 更新 server 端
    print(f"{user}")
    print(f"is enrolled successfully.")
    return jsonify(user.to_dict()), 200

@app.route("/create/<int:room>", methods=["POST"])
def create(room: int):
    global clients, rooms
    try:
        user = PERSON.to_obj(request.json)
    except Exception as e:
        print(f"Error parsing user: {e}")
        return jsonify({"message": "Invalid user json"}), 400
    if room < 0 or room >= len(rooms):
        return jsonify({"message": "Invalid room ID"}), 400
    if user.room is not None:
        print(f"{user.name}.room != None")
        return jsonify({"message": "You are already in a room."}), 400
    if rooms[room].ID:
        print(f"rooms[{room}].ID = {rooms[room].ID}")
        return jsonify({"message": "The room has already been created."}), 400
    # Update states
    user.room = room                # 更新使用者房間編號
    user.index = 0                  # 使用者是該房間的第一個 client
    clients[user.ID] = user         # 更新 server 端
    rooms[room].ID = [user.ID]      
    rooms[room].data = [DATA(ID=user.ID, name=user.name, index=0)]
    rooms[room].present = [True]
    print(f"{user.name}")
    print(f"create {room}")
    print(f"successfully.")
    # Return response
    return jsonify({"user": user.to_dict(), "room": rooms[room].to_dict()}), 200
        
@app.route("/invite/<Uname>", methods=["POST"])
def invite(Uname:str):                  # 被邀請人的 name, 邀請至使用者當前所在的 room
    global clients, rooms
    try:
        user = PERSON.to_obj(request.json)
    except Exception as e:
        print(f"Error parsing user: {e}")
        return jsonify({"message": "Invalid user json"}), 400
    if user is None:
        return jsonify({"message": "Invalid User json."}), 400
    if user.room is None:
        return jsonify({"message": "You are not in any room."}), 400
    if user.room<0 or user.room>=4:
        return jsonify({"message": "invalid Room ID"}), 400
    print(f"{user.name} invites {Uname} into rooms[{user.room}]")
    room = rooms[user.room]
    if user.ID not in room.ID:
        return jsonify({"message": "No inviting privilege."}), 400
    for index, client in enumerate(clients):
        if client.valid and client.name == Uname:
            invitee = client
            break
        if index == 7:
            return jsonify({"message": f"{Uname} not found"}), 404
    amount = len(room.ID)
    room.ID.append(invitee.ID)
    room.data.append(DATA(ID=invitee.ID, name=invitee.name, index=amount))
    room.present.append(False)
    print(f"{user}")
    print(f"invite")
    print(f"{invitee}")
    print(f"to {room}")
    print(f"successfully.")
    return jsonify({"user": user.to_dict(), "room": room.to_dict()}), 200

@app.route("/search/<int:RID>", methods=["POST"])
def search(RID:int):
    global clients, rooms
    try:
        user = PERSON.to_obj(request.json)
    except Exception as e:
        print(f"Error parsing user: {e}")
        return jsonify({"message": "Invalid user json"}), 400
    if RID<0 or RID>=4:
        return jsonify({"message": "Invalid Room ID"}), 400
    room = rooms[RID]
    print(f"{user}")
    print(f"is searching for")
    print(f"{room}")
    if not user.ID in room.ID:              # 沒有在邀請名單上
        print(f"{user.name} didn't get into room {RID}")
        return jsonify({"message": "You have not been invited yet"}), 400
    index = room.ID.index(user.ID)          # index = user 在該房間的順序
    user.room = RID                         # 更新 user 的 room 編號
    user.index = index                      # 是該房間的第 index 個 client
    clients[user.ID] = user                 # 更新 server 端
    room.present[index] = True              # 房間第 index 個人出席
    print(f"{user.name}")
    print(f"enter {room}")
    return jsonify({"user": user.to_dict(), "room": room.to_dict()}), 200

@app.route("/watch/<int:ID>", methods=["POST"])
def watch(ID:int):
    global clients, rooms
    client = clients[ID]
    try:
        data = DATA.to_obj(request.json)
    except Exception as e:
        print(f"Error parsing data: {e}")
        return jsonify({"message": "Invalid data json"}), 400
    try:
        room = rooms[client.room]
    except Exception as e:
        print(f"Error Room ID: {e}")
        return jsonify({"message": "Invalid Room ID"}), 400
    room.data[client.index] = data      # 把 user 資料放到 room 裡面
    if client.index==0:
        if len(room.ID)>1:
            return jsonify(room.data[1].to_dict()), 200
        else:
            return jsonify(data.to_dict()), 200
    elif client.index==1:
        return jsonify(room.data[0].to_dict()), 200

if __name__ == "__main__":
    # port = int(input("Enter the port number for the server: "))
    S10()
    app.run(port=6000)
