from flask import Flask, request, jsonify
from share import PERSON, DATA, ROOM
import copy

app = Flask(__name__)
clients = [PERSON(ID=index) for index in range(8)]
rooms = [ROOM() for index in range(4)]

@app.route("/bye", methods=["POST"])
def bye():
    global clients, rooms
    user = PERSON.to_obj(request.json)
    if user.ID<0 or user.ID>=8:
        return jsonify({"message": f"Invalid ID {user.ID}"}), 400
    room = rooms[user.room]     # 如果正在視訊 是否 需要斷開連結
    clients[user.ID] = PERSON()
    user.name = "bye"
    print(f"clients[{user.ID}] clear")
    return jsonify(user.to_dict()), 200

@app.route("/enroll", methods=["POST"])
def enroll():
    global clients, rooms
    user = PERSON.to_obj(request.json)
    for index, client in enumerate(clients):
        if not user.valid and not client.valid:  # 還沒找到 and 這格沒有使用者佔走
            user.ID = index
            user.valid = True
        if client.name == user.name:             # handle once find repeat name
            return jsonify({"message": "The name has existed already."}), 400
    if not user.valid:                           # no repeat name = no available quota
        return jsonify({"message": "There is no available space for clients."}), 503
    clients[user.ID].valid = user.valid
    clients[user.ID].name = user.name
    clients[user.ID].WH = user.WH
    print(f"{user} has been enrolled.")
    return jsonify(user.to_dict()), 200

@app.route("/create/<int:room>", methods=["POST"])
def create(room:int):
    global clients, rooms
    user = PERSON.to_obj(request.json)
    print(f"{user} create room {room}")
    if not user.room == None:
        return jsonify({"message": "You have being in a room already."}), 400
    if len(rooms[room].ID):
        return jsonify({"message": "The room has been created already."}), 400
    user.room = room
    rooms[room].ID.append(user.ID)
    rooms[room].data.append(DATA(ID=user.ID,index=0))
    rooms[room].present.append(True)
    return jsonify({"user":user.to_dict(), "room":rooms[room].to_dict()}), 200
        
@app.route("/invite/<Uname>", methods=["POST"])
def invite(Uname:str):           # 被邀請人的 name, 邀請至哪一個 room
    global clients, rooms
    user = PERSON.to_obj(request.json)
    if user.room == None:
        return jsonify({"message": "You are not in any room."}), 400
    print(f"{user.name} invites {Uname} into room {user.room}")
    if user.room<0 or user.room>=4:
        return jsonify({"message": "invalid Room ID"}), 400
    room = rooms[user.room]
    print(f"user = {user}")
    print(f"room = {room}")
    if user == None or room == None:
        return jsonify({"message": "data missed"}), 400
    if user.ID not in room.ID:
        return jsonify({"message": "No inviting privilege in this room."}), 400
    for index, client in enumerate(clients):
        if client.valid and client.name == Uname:
            UID = client.ID
            break
        if index == 7:
            return jsonify({"message": f"{Uname} not found"}), 404
    print(f"user = {user}")
    print(f"room = {room}")
    
    amount = len(room.ID)
    room.ID.append(UID)
    print(f"{room.ID} append {UID}")
    room.data.append(DATA(ID=UID,index=amount))
    room.present.append(False)
    return jsonify({"user": user.to_dict(), "room": room.to_dict()}), 200

@app.route("/search/<int:RID>", methods=["POST"])
def search(RID:int):
    global clients, rooms
    user = PERSON.to_obj(request.json)
    print(f"{user} is searching for room id = {RID}")
    room = rooms[RID]
    print(f"search list user id in room = {room.ID}")
    if not user.ID in room.ID:          # 沒有在邀請名單上
        print(f"{user.name} didn't get into room {RID}")
        return jsonify({"message": "You have not been invited yet"}), 400
    else:                               # 成功進入到 被邀請的房間
        index = room.ID.index(user.ID)  # index = user 在該房間的順序
        user.room = RID                 # 更新 user 的 room 編號
        clients[user.ID] = user         # 
        room.present[index] = True      # 房間第 index 個人出席
        print(f"{user.name} enter room {RID}")
        return jsonify({"user": user.to_dict(), "room": room.to_dict()}), 200
        

if __name__ == "__main__":
    # port = int(input("Enter the port number for the server: "))
    app.run(debug=True, port=6000)
