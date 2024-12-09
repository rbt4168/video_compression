from typing import List

class PERSON:
    def __init__(self,
                 ID:int=0,                      #
                 name:str="",                   # 代表自己的稱呼
                 talk:int=None,                 # 代表在跟誰對話
                 room:int=None,                 # 代表正在哪一個群組
                 point:tuple[int, int]=(0, 0),  # 代表滑鼠指向哪裡
                 WH:tuple[int, int]=(0, 0),     # 代表自己的畫面 寬W 和 高H
                 mosaic:List[List[int]]=[],     # 馬賽克的資料 16 * 16 * 3
                 detail:List[List[int]]=[],     # 細節的資料，對方滑鼠指向的位置附近的資料
                 valid:bool=False):             # 有沒有人在用 True代表有人在用
        self.ID = ID
        self.name = name
        self.room = room
        self.WH = WH
        self.talk = talk
        self.point = point
        self.mosaic = mosaic
        self.detail = detail
        self.valid = valid

    def to_dict(self):
        """Converts the object to a dictionary."""
        return {
            "ID": self.ID,
            "name": self.name,
            "room": self.room,
            "talk": self.talk,
            "point": self.point,
            "WH": self.WH,
            "mosaic": self.mosaic,
            "detail": self.detail,
            "valid": self.valid
        }

    @classmethod
    def to_obj(cls, data):
        """Creates an object from a dictionary."""
        return cls(
            ID=data.get("ID", 0),
            name=data.get("name", "NoName"),
            room=data.get("room", 0),
            talk=data.get("talk", 0),
            point=tuple(data.get("point", (0, 0))),
            WH=tuple(data.get("WH", (0, 0))),
            mosaic=data.get("mosaic", []),
            detail=data.get("detail", []),
            valid=data.get("valid", False)
        )

    def __str__(self):
        return f"ID: {self.ID}, name: {self.name}, room: {self.room}, talk: {self.talk}, point: {self.point}, WH: {self.WH}."
    



class DATA():
    def __init__(self,
                 ID:int=0,
                 name:str="",
                 index:int=0,                   # 在房間裡面的index
                 WH:tuple[int, int]=(0, 0),     # 代表自己的畫面 寬W 和 高H
                 point:tuple[int, int]=(0, 0),  # 關注的點
                 mosaic:List[List[int]]=[],     # 模糊資料
                 detail:List[List[int]]=[],     # 細節資料
                 valid:bool=False):
        self.ID = ID
        self.name = name
        self.index = index
        self.WH = WH
        self.point = point
        self.mosaic = mosaic
        self.detail = detail
        self.valid = valid

    def to_dict(self):
        return {
            "ID": self.ID,
            "name": self.name,
            "index": self.index,
            "WH": self.WH,
            "point": self.point,
            "mosaic": self.mosaic,
            "detail": self.detail,
            "valid": self.valid
        }
    
    @classmethod
    def to_obj(cls, data):
        return cls(
            ID=data.get("ID", 0),
            name=data.get("name", ""),
            index=data.get("index", 0),
            WH=tuple(data.get("WH", (0, 0))),
            point=tuple(data.get("point", (0, 0))),
            mosaic=data.get("mosaic", []),
            detail=data.get("detail", []),
            valid=data.get("valid", False)
        )




class ROOM():
    def __init__(self,
                 ID:List[int]=[],
                 data:List[DATA]=[],
                 present:List[bool]=[]):
        self.ID = ID
        self.data = data
        self.present = present

    def to_dict(self):
        return {
            "ID": self.ID,
            "data": [d.to_dict() for d in self.data],
            "present": self.present
        }
    
    @classmethod
    def to_obj(cls, room_data):
        """Create a ROOM object from a dictionary."""
        return cls(
            ID=room_data.get("ID", []),
            data=[DATA.to_obj(d) for d in room_data.get("data", [])],
            present=room_data.get("present", [])
        )

    def __str__(self):
        id_string = " and ".join(map(str, self.ID)) if self.ID else "No IDs"
        return f"{id_string} are seeing each other"
        return f"{self.ID[0]} and {self.ID[1]} are seeing valid={self.valid}"
