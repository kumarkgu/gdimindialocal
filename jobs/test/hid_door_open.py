import requests
from requests.auth import HTTPBasicAuth
import json


class HIDApis:
    def __init__(self):
        # self.api = 'https://localhost:61960/api/DoorControls'
        # self.api = 'http://localhost:61960/api/DoorControls'
        self.api = 'http://192.168.1.200/AccessAPI/api/DoorControls'
        self.headers = {
            "Content-Type": "application/json;charset=utf-8"
        }
        self.username = 'apiadmin'
        self.password = 'apiadmin'

    def get_door_list(self):
        response = requests.get(url=self.api, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
        print(response)
        if response.status_code == requests.codes.ok:
            print(response.content)

    def open_door(self, doorid, option=0):
        data = [{
            "DoorId": doorid,
            "Type": option
        }]
        response = requests.post(
            url=self.api,
            data=json.dumps(data),
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password)
        )
        # print(response.json())


def test_hid():
    hidobj = HIDApis()
    hidobj.get_door_list()
    # hidobj.open_door(12, 0)
    # hidobj.open_door(12, 1)
    # hidobj.open_door(2036, 0)
    # hidobj.open_door(2036, 1)
    # hidobj.open_door(2035, 1)  # our door
    # hidobj.open_door(2034, 0)  # Reception behind door


test_hid()


# [
#     {"DoorId":3,"Name":"Door-pune-V2000(Demo)-Reader1"},
#     {"DoorId":4,"Name":"Door-pune-V2000(Demo)-Reader2"},
#     {"DoorId":5,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-48 LOCKER READER-1 & 48 LOCKER READER-2"},
#     {"DoorId":6,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-FIRE EXIT DOOR & FIRE EXIT DOOR"},
#     {"DoorId":8,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-FIRE EXIT DOOR & FIRE EXIT DOOR"},
#     {"DoorId":9,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-18 LOCKER READER-1 & 18 LOCKER READER-2"},
#     {"DoorId":10,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-IT STORE ROOM & IT STORE ROOM"},
#     {"DoorId":11,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-SERVICE LIFT & SERVICE LIFT"},
#     {"DoorId":13,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-Reader1 & Reader2"},
#     {"DoorId":15,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-18 LOCKER READER-1 & 18 LOCKER READER-2"},
#     {"DoorId":17,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-IT STORE ROOM & IT STORE ROOM"},
#     {"DoorId":18,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-SERVICE LIFT & SERVICE LIFT"},
#     {"DoorId":19,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-SERVER ROOM & SERVER ROOM"},
#     {"DoorId":2024,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-120 LOCKER READER-1 & 120 LOCKER READER-2"},
#     {"DoorId":2029,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-UPS ROOM PASSAGE LOCKERS IN & UPS ROOM PASSAGE LOCKERS OUT"},
#     {"DoorId":12,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-RECEPTION RIGHT SIDE DOOR & NEAR UPS ROOM LOCKR"},
#     {"DoorId":2034,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-RECEPTION RIGHT SIDE DOOR IN & RECEPTION RIGHT SIDE DOOR OUT"},
#     {"DoorId":2035,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-RECEPTION LEFT SIDE DOOR IN & RECEPTION LEFT SIDE DOOR OUT"},    -- our door
#     {"DoorId":2036,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-RECEPTION RIGHT SIDE DOOR"},
#     {"DoorId":2037,"Name":"Door-2-V1000 EVO(MAIN PANEL IC)-28 LOCKER READER"}
# ]
