import re
from datetime import datetime
import os
from collections import defaultdict


def extract_classrooms(file_path):
    classrooms = defaultdict(list)  # 使用 defaultdict 来存储列表
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):  # 使用 enumerate 进行行遍历
            match = re.search(
                r"课程名称: (.+?), 考试时间: (\d{4}-\d{2}-\d{2} \d{2}:\d{2})~(\d{2}:\d{2}), 考场: (\S+)",
                line,
            )
            if match:
                subject = match.group(1)
                start_time_str = match.group(2)
                end_time_str = f"{start_time_str[:11]}{match.group(3)}"
                classroom = match.group(4)
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                classrooms[classroom].append(
                    (start_time, end_time, subject)
                )  # 将考试信息添加到列表中
                # print(classroom, classrooms[classroom])
            else:
                print(f"Line {line_number}: No match found")
    return classrooms


def get_upcoming_classrooms(classrooms, building_name, current_time):
    upcoming_classrooms = {}
    ongoing_classrooms = {}  # 新增：用于存储正在进行的考试
    for classroom, exams in classrooms.items():
        for start_time, end_time, subject in exams:
            if start_time.date() == current_time.date() and building_name in classroom:
                if start_time <= current_time <= end_time:
                    # 当前时间正在进行的考试
                    if classroom not in ongoing_classrooms:
                        ongoing_classrooms[classroom] = []
                    ongoing_classrooms[classroom].append(
                        (start_time, end_time, subject)
                    )
                elif start_time > current_time:
                    # 即将开始的考试
                    if classroom not in upcoming_classrooms:
                        upcoming_classrooms[classroom] = []
                    upcoming_classrooms[classroom].append(
                        (start_time, end_time, subject)
                    )
    return ongoing_classrooms, upcoming_classrooms


def get_tomorrow_classrooms(classrooms, building_name, current_time):
    tomorrow_classrooms = {}
    next_day = current_time.replace(day=current_time.day + 1)
    for classroom, exams in classrooms.items():
        for start_time, end_time, subject in exams:
            if start_time.date() == next_day.date() and building_name in classroom:
                if classroom not in tomorrow_classrooms:
                    tomorrow_classrooms[classroom] = []
                tomorrow_classrooms[classroom].append((start_time, end_time, subject))
    return tomorrow_classrooms


def group_classrooms_by_time(classrooms):
    time_groups = defaultdict(list)
    for classroom, exams in classrooms.items():
        for start_time, end_time, _ in exams:
            time_groups[(start_time, end_time)].append(classroom)
    return time_groups


def main():
    # 提取教室信息
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "exam_info.txt"
    )

    classrooms = extract_classrooms(file_path)

    # 获取用户输入的教学楼名称
    building_name = "致知楼"
    current_time = datetime(2025, 1, 3, 23, 11, 34)  # 获取当前时间

    # 获取该教学楼今日内往后时间还有考场的教室
    upcoming_classrooms = get_upcoming_classrooms(
        classrooms, building_name, current_time
    )

    if upcoming_classrooms:
        print(f"当前时间：{current_time}")
        time_groups = group_classrooms_by_time(upcoming_classrooms)
        for (start_time, end_time), rooms in time_groups.items():
            room_list = ", ".join(rooms)
            print(
                f"{room_list} 将在 {start_time.strftime('%H:%M')} 至 {end_time.strftime('%H:%M')} 进行考试"
            )
    else:
        print(f"当前时间：{current_time},在【{building_name}】没有考场教室")
        print(f"【{building_name}】今日内没有即将开始的考场教室，将获取明天的考场教室")

        # 获取该教学楼明天的考场教室
        tomorrow_classrooms = get_tomorrow_classrooms(
            classrooms, building_name, current_time
        )

        if tomorrow_classrooms:
            print(f"【{building_name}】明天的考场教室安排如下：")
            time_groups = group_classrooms_by_time(tomorrow_classrooms)
            for (start_time, end_time), rooms in time_groups.items():
                room_list = ", ".join(rooms)
                print(
                    f"{room_list} 将在 {start_time.strftime('%H:%M')} 至 {end_time.strftime('%H:%M')} 进行考试"
                )
        else:
            print(f"【{building_name}】明天没有考场教室安排")


if __name__ == "__main__":
    main()
