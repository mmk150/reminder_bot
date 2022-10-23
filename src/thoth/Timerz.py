import json
from enum import IntEnum


class Timerz:
    req_time: str
    ping_time: str
    user_id: str
    del_code: str
    channel: str
    message: str
    badgermode: str

    def __init__(self, ping_time, req_time, user_id, del_code, channel, message, badgermode):
        self.ping_time = ping_time
        self.req_time = req_time
        self.user_id= user_id
        self.del_code = del_code
        self.channel = channel
        self.message = message
        self.badgermode = badgermode

    def to_string(self) -> str:
        return json.dumps(self.__dict__)

    @staticmethod
    def from_string(data: str):
        return Timerz(**json.loads(data))


def roundtrip_example(string_in_db: str):

    my_timer = Timerz.from_string(string_in_db)
    string_for_db = my_timer.to_string()

    assert string_for_db == string_in_db
