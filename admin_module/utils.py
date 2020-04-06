from datetime import datetime
import typing


def remove_id_from_set(set_object: typing.Set[typing.Tuple[int, datetime]], member_id: int):
    set_copy = set_object.copy()
    for member_date in set_copy:
        if member_date[0] == member_id:
            set_object.remove(member_date)
            print("Removed {} from set".format(member_date[0]))
