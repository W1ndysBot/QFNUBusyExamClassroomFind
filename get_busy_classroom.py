import re
from datetime import datetime
import os
from collections import defaultdict


def extract_classrooms(file_path):
    classrooms = {}
    seen_lines = set()  # 用于记录已经处理过的行
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line in seen_lines:
                # print(f"重复行: {line.strip()}")  # 输出重复行
                continue
            seen_lines.add(line)
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
                classrooms[classroom] = (start_time, end_time, subject)
    return classrooms


def query_classrooms(classrooms, building_name, current_time):
    busy_classrooms = []
    for classroom, (start_time, end_time, subject) in classrooms.items():
        if building_name in classroom and start_time <= current_time <= end_time:
            room_number = classroom.replace(building_name, "").strip()
            busy_classrooms.append((room_number, subject))
    return busy_classrooms


def get_upcoming_classrooms(classrooms, building_name, current_time):
    upcoming_classrooms = []
    for classroom, (start_time, end_time, subject) in classrooms.items():
        if building_name in classroom and start_time > current_time:
            room_number = classroom.replace(building_name, "").strip()
            upcoming_classrooms.append((room_number, subject, start_time, end_time))
    return upcoming_classrooms


def group_classrooms_by_time(upcoming_classrooms):
    time_groups = defaultdict(list)
    for room, subject, start, end in upcoming_classrooms:
        time_range = (start.strftime("%H:%M"), end.strftime("%H:%M"))
        time_groups[time_range].append(room)
    return time_groups


# 提取教室信息
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exam_info.txt")
classrooms = extract_classrooms(file_path)

# 查询某个楼的教室
building_name = "综合教学楼"  # 你可以根据需要更改
current_time = datetime.now()  # 获取当前时间
busy_classrooms = query_classrooms(classrooms, building_name, current_time)

# 获取今日内往后时间还有考场的教室
upcoming_classrooms = get_upcoming_classrooms(classrooms, building_name, current_time)

# 按时间段分组教室
time_grouped_classrooms = group_classrooms_by_time(upcoming_classrooms)

# 输出结果
if busy_classrooms:
    room_numbers = ", ".join([room for room, _ in busy_classrooms])
    print(f"{building_name}的有考场教室：{room_numbers}")
else:
    print(f"{building_name}没有考场教室。")

if time_grouped_classrooms:
    for (start_time, end_time), rooms in time_grouped_classrooms.items():
        room_list = ", ".join(rooms)
        print(f"{building_name}的 {room_list} 将在 {start_time} 至 {end_time} 进行考试。")
else:
    print(f"{building_name}今日内没有即将开始的考场教室。")

