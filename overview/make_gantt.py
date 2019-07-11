import datetime
import pandas as pd
from itertools import groupby
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, Range1d
from bs4 import BeautifulSoup
from django.utils import timezone
import os

import time

# process_list = [
#     ('breakfast',
#      datetime.datetime(2019, 6, 1, 7, 15),
#      datetime.datetime(2019, 6, 1, 7, 55), 'decimal'
#      ),
#     ('walking',
#      datetime.datetime(2019, 6, 1, 8, 15),
#      datetime.datetime(2019, 6, 1, 10, 55), 'decimal'
#      ),
#     ('sleeping',
#      datetime.datetime(2019, 6, 1, 11, 15),
#      datetime.datetime(2019, 6, 1, 12, 55), 'decimal'
#      ),
#     ('Hotel_Boot',
#      datetime.datetime(2019, 6, 1, 20, 50),
#      datetime.datetime(2019, 6, 2, 12, 0), 'decimal'
#      ),
#     ('dinner',
#      datetime.datetime(2019, 6, 1, 13, 15),
#      datetime.datetime(2019, 6, 1, 14, 55), 'decimal'
#      ),
#     ('breakfast',
#      datetime.datetime(2019, 6, 2, 7, 15),
#      datetime.datetime(2019, 6, 2, 7, 55), 'decimal'
#      ),
#     ('dinner',
#      datetime.datetime(2019, 6, 2, 13, 15),
#      datetime.datetime(2019, 6, 2, 14, 55), 'decimal'
#      ),
#     ('breakfast',
#      datetime.datetime(2019, 6, 4, 7, 15),
#      datetime.datetime(2019, 6, 4, 7, 55), 'decimal'
#      ),
#     ('dinner',
#      datetime.datetime(2019, 6, 4, 13, 15),
#      datetime.datetime(2019, 6, 4, 14, 55), 'decimal'
#      ),
#     ('walk_ex',
#      datetime.datetime(2019, 6, 2, 15, 15),
#      datetime.datetime(2019, 6, 2, 19, 0), 'decimal'
#      ),
#     ('a_photo_session',
#      datetime.datetime(2019, 6, 4, 9, 30),
#      datetime.datetime(2019, 6, 5, 12, 0), 'decimal'
#      ),
#     ('wine_museum',
#      datetime.datetime(2019, 6, 4, 16, 0),
#      datetime.datetime(2019, 6, 6, 10, 30), 'decimal')
# ]


def unpack_lists(lists_in_list: list) -> list:
    unpacked_list = []
    for elem in lists_in_list:
        if type(elem[0]) is str:
            unpacked_list.append(elem)
        else:
            unpacked_list.extend(elem)
    return unpacked_list


def partition_proc(event: list) -> list:
    """ Функция дробления многодневных процессов и их сортировки по времени начала процесса"""
    event_title = event[0]
    begin_event = min(event[1:])
    end_event = max(event[1:])

    delta = end_event.day - begin_event.day
    if delta != 0:
        point = begin_event
        temp_list = []
        time_end = datetime.time(23, 59)        # Все суточные процессы заканиваются в полночь

        for _ in range(delta):
            temp_list.append([
                event_title,
                point,
                datetime.datetime.combine(point.date(), time_end, tzinfo=timezone.utc)
            ])

            point = datetime.datetime.combine(
                point.date(),
                time_end,
                tzinfo=timezone.utc
            ) + datetime.timedelta(minutes=1)
        temp_list.append([event_title, point, end_event])

        return temp_list
    return [event_title, begin_event, end_event]


def valid_process(process: list) -> bool:
    for elem in process:
        if elem is None:
            return False
    return True


def main(process_list) -> list:
    valid_process_list = []
    for process in process_list:
        process = list(process)
        if valid_process(process):
            valid_process_list.append(partition_proc(process))

    process_list = unpack_lists(valid_process_list)
    return sorted(process_list, key=lambda x: x[1])


def diagram_drow_in_file(day_proc: list, url: str):
    # Рисует диаграмму Ганта и сохраняет ее в файл

    DF = pd.DataFrame(columns=['Process', 'Start', 'End'])
    diagram_title = str(day_proc[0][1].date().strftime('%d.%m.%Y'))
    for i, data in enumerate(day_proc[::-1]):
        DF.loc[i] = data
    G = figure(
        title=diagram_title,
        x_axis_type='datetime',
        width=300,
        height=120,
        y_range=DF.Process.tolist(),
        x_range=Range1d(
            DF.Start.min() - datetime.timedelta(hours=1),
            DF.End.max() + datetime.timedelta(hours=1))
    )
    DF['ID'] = DF.index + 0.75
    DF['ID1'] = DF.index + 0.25
    CDS = ColumnDataSource(DF)
    G.quad(
        left='Start',
        right='End',
        bottom='ID',
        top='ID1',
        source=CDS,
        line_width=3)
    output_file(url)
    save(G)


def parsing_file(url) -> str:
    with open(url) as html:
        soup = BeautifulSoup(html, 'html.parser')
    return str(soup.body.find_all(['div', 'script']))[1:-1]


def start_gantt(original_list):
    url = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gantt.html')
    diagrams = ''
    correct_process_list = main(original_list)
    correct_process_list = [
        list(elem) for _, elem in groupby(
            correct_process_list,
            lambda x: x[1].day
        )
    ]

    # # Проверка вывода процессов
    # for i in correct_process_list:
    #     for k in i:
    #         print(k)

    for day_proc in correct_process_list:
        diagram_drow_in_file(day_proc, url)
        # Если диаграмма не будет успевать отрисовываться - установить достаточную временную задержку
        # time.sleep(0.8)
        diagrams += parsing_file(url)
    return diagrams


# ### Запуск тела программы

if __name__ == '__main__':
    diagrams_list = start_gantt(process_list)


# #### Просмотр результатов вывода в файле (можно кидать в html-документ)
# with open('result_parse.txt', 'w') as file:
# #     file.write('<HEAD>:\n', diagrams_list[0]['head'], '\n</HEAD>')
#    for i in range(len(diagrams_list)):
#        file.write(diagrams_list[i]['body'])
