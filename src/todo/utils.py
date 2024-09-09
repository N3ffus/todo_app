from enum import Enum


class StatusEnum(Enum):
    not_started = "0"
    in_progress = "1"
    completed = "2"


class SortingEnum(Enum):
    by_date = "0"
    by_title = "1"
    by_status = "2"


def get_last_page(tasks_cnt, limit):
    return (tasks_cnt + limit - 1) // limit


def get_pages_list(tasks_cnt: int, cur_page: int, limit: int) -> list[int] | None:
    pages_cnt = (tasks_cnt + limit - 1) // limit
    next_cnt = pages_cnt - cur_page

    if cur_page <= 3:
        return [i for i in range(1, min(pages_cnt, 5) + 1)]

    if next_cnt >= 2:
        return [i for i in range(cur_page - 2, cur_page + 3)]
    elif next_cnt == 1:
        return [i for i in range(cur_page - 3, cur_page + 2)]
    else:
        return [i for i in range(cur_page - 4, cur_page + 1)]
