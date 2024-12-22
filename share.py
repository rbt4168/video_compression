from typing import List
import numpy as np
import cv2

class PERSON:
    def __init__(self,
                 ID:int=0,                      #
                 name:str="",                   # 代表自己的稱呼
                 index:int=0,                   # 代表在房間的編號
                 room:int=None,                 # 代表正在哪一個群組
                 valid:bool=False):             # 有沒有人在用 True代表有人在用
        self.ID = ID
        self.name = name
        self.index = index
        self.room = room
        self.valid = valid

    def to_dict(self):
        """Converts the object to a dictionary."""
        return {
            "ID": self.ID,
            "name": self.name,
            "index": self.index,
            "room": self.room,
            "valid": self.valid
        }

    @classmethod
    def to_obj(cls, data):
        """Creates an object from a dictionary."""
        return cls(
            ID=data.get("ID", 0),
            name=data.get("name", "NoName"),
            index=data.get("index", 0),
            room=data.get("room", 0),
            valid=data.get("valid", False)
        )

    def __str__(self):
        return f"User( ID: {self.ID}, name: {self.name}, index: {self.index}, room: {self.room})"
    


class DATA:
    def __init__(self,
                 ID:int=0,
                 name:str="",
                 index:int=0,
                 grid:int=0,
                 WH:tuple[int, int]=(0, 0),
                 watch:int=0,
                 point:tuple[int, int]=(0, 0),
                 seen:tuple[tuple[int, int], tuple[int, int]]=((0, 0), (0, 0)),
                 mosaic:List[List[List[int]]]=None,
                 detail:List[List[List[int]]]=None,
                 valid:bool=False):
        self.ID = ID
        self.name = name
        self.index = index
        self.grid = grid
        self.WH = WH
        self.watch = watch
        self.point = point
        self.seen = seen
        self.mosaic = mosaic if mosaic is not None else []
        self.detail = detail if detail is not None else []
        self.valid = valid

    def to_dict(self):
        return {
            "ID": self.ID,
            "name": self.name,
            "index": self.index,
            "grid": self.grid,
            "WH": self.WH,
            "watch": self.watch,
            "point": self.point,
            "seen": self.seen,
            "mosaic": self.mosaic.tolist() if isinstance(self.mosaic, np.ndarray) else self.mosaic,
            "detail": self.detail.tolist() if isinstance(self.detail, np.ndarray) else self.detail,
            "valid": self.valid
        }
    @classmethod
    def to_obj(cls, data):
        return cls(
            ID=data.get("ID", 0),
            name=data.get("name", ""),
            index=data.get("index", 0),
            grid=data.get("grid", 0),
            WH=tuple(data.get("WH", (0, 0))),
            watch=data.get("watch", 0),
            point=tuple(data.get("point", (0, 0))),
            seen=tuple(data.get("seen", (0, 0))),
            mosaic=np.array(data.get("mosaic", [])) if isinstance(data.get("mosaic", []), list) else data.get("mosaic"),
            detail=np.array(data.get("detail", [])) if isinstance(data.get("detail", []), list) else data.get("detail"),
            valid=data.get("valid", False)
        )
    
    def __str__(self):
        return (f"Data( ID: {self.ID},  name: {self.name}, index: {self.index})\n"
                f"    ( watch: {self.watch}, point: {self.point})\n"
                f"    ( seen: {self.seen}, grid: {self.grid})")


class ROOM():
    def __init__(self,
                 RID:int=0,
                 ID:List[int]=[],
                 data:List[DATA]=[],
                 present:List[bool]=[]):
        self.RID = RID
        self.ID = ID
        self.data = data
        self.present = present

    def to_dict(self):
        return {
            "RID": self.RID,
            "ID": self.ID,
            "data": [d.to_dict() for d in self.data],
            "present": self.present
        }
    
    @classmethod
    def to_obj(cls, room_data):
        """Create a ROOM object from a dictionary."""
        return cls(
            RID=room_data.get("RID", 0),
            ID=room_data.get("ID", []),
            data=[DATA.to_obj(d) for d in room_data.get("data", [])],
            present=room_data.get("present", [])
        )

    def __str__(self):
        id_string = ", ".join(map(str, self.ID)) if self.ID else "No IDs"
        return f"Room( RID={self.RID}, ID= {id_string})"
