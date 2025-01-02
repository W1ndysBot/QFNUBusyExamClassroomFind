# script/QFNUBustExamClassroomFind/main.py

import logging
import os
import re
import sys
from datetime import datetime

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import *
from app.api import *
from app.switch import load_switch, save_switch
from app.scripts.QFNUBustExamClassroomFind.get_busy_classroom import (
    extract_classrooms,
    query_classrooms,
    get_upcoming_classrooms,
    group_classrooms_by_time,
)

# 数据存储路径,实际开发时,请将QFNUBustExamClassroomFind替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "QFNUBustExamClassroomFind",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "QFNUBustExamClassroomFind")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "QFNUBustExamClassroomFind", status)


# 处理开关状态
async def toggle_function_status(websocket, group_id, message_id, authorized):
    if not authorized:
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌你没有权限对曲阜师范大学期末考试考场教室查询功能进行操作,请联系管理员。",
        )
        return

    if load_function_status(group_id):
        save_function_status(group_id, False)
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]🚫🚫🚫曲阜师范大学期末考试考场教室查询功能已关闭",
        )
    else:
        save_function_status(group_id, True)
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]✅✅✅曲阜师范大学期末考试考场教室查询功能已开启\n"
            "开启后,本群内成员可以查询曲阜师范大学期末考试考场教室信息。\n"
            "使用方法：群内发送“xxx考场”,即可查询xxx考场的教室信息,例如：\n"
            "群内发送“综合教学楼考场”,即可查询综合教学楼考场的教室信息。注意教室应以教务系统命名为准，尽量不要用简称和俗语，如综合教学楼，JA等",
        )


# 处理考场信息
async def process_exam_classroom_info(websocket, group_id, message_id, raw_message):
    # 教学楼全称到简称的映射
    building_name_map = {
        "综合教学楼": ["综合楼"],
        "生物楼": ["生科楼", "生科"],
        "数学楼": ["数科楼"],
        "实验中心": ["田家炳实验楼", "实验楼"],
        "JA": ["A楼", "a楼", "JA楼"],
        "JB": ["B楼", "b楼", "JB楼"],
        "JC": ["C楼", "c楼", "JC楼"],
        "JD": ["D楼", "d楼", "JD楼"],
        "JE": ["E楼", "e楼", "JE楼"],
        "JF": ["F楼", "f楼", "JF楼"],
        "JG": ["G楼", "g楼", "JG楼"],
        "JH": ["H楼", "h楼", "JH楼"],
        "JI": ["I楼", "i楼", "JI楼"],
        "JJ": ["J楼", "j楼", "JJ楼"],
        "JK": ["K楼", "k楼", "JK楼"],
        "JL": ["L楼", "l楼", "JL楼"],
        "JM": ["M楼", "m楼", "JM楼"],
        "JN": ["N楼", "n楼", "JN楼"],
        "JO": ["O楼", "o楼", "JO楼"],
        "JP": ["P楼", "p楼", "JP楼"],
        "JQ": ["Q楼", "q楼", "JQ楼"],
        "JR": ["R楼", "r楼", "JR楼"],
        "JS": ["S楼", "s楼", "JS楼"],
        "JT": ["T楼", "t楼", "JT楼"],
        "JU": ["U楼", "u楼", "JU楼"],
        "JV": ["V楼", "v楼", "JV楼"],
        "JW": ["W楼", "w楼", "JW楼"],
        "JX": ["X楼", "x楼", "JX楼"],
        "JY": ["Y楼", "y楼", "JY楼"],
        "JZ": ["Z楼", "z楼", "JZ楼"],
        # 添加更多映射
    }

    match = re.match(r"(.*)考场", raw_message)
    if match:
        input_name = match.group(1)

        # 转换为全大写字母
        building_name = input_name.upper()

        # 查找全称
        for full_name, aliases in building_name_map.items():
            if input_name in aliases:
                building_name = full_name
                break

        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "exam_info.txt"
        )
        classrooms = extract_classrooms(file_path)
        current_time = datetime.now()  # 获取当前时间，精确到秒
        busy_classrooms = query_classrooms(classrooms, building_name, current_time)
        upcoming_classrooms = get_upcoming_classrooms(
            classrooms, building_name, current_time
        )
        time_grouped_classrooms = group_classrooms_by_time(upcoming_classrooms)
        message_parts = []

        if busy_classrooms:
            room_numbers = ", ".join([room for room, _ in busy_classrooms])
            message_parts.append(
                f"当前时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')},在【{building_name}】有考场教室：{room_numbers}\n\n"
            )
        else:
            message_parts.append(
                f"当前时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')},在【{building_name}】没有考场教室\n\n"
            )

        if time_grouped_classrooms:
            for (
                start_time,
                end_time,
            ), rooms in time_grouped_classrooms.items():
                room_list = ", ".join(rooms)
                message_parts.append(
                    f"【{building_name}】的 {room_list} 将在 {start_time} 至 {end_time} 进行考试\n"
                )
        else:
            message_parts.append(
                f"【{building_name}】今日内没有即将开始的考场教室或教学楼名字不存在\n请注意教室名称以教务系统为准，尽量不要用简称和俗语，如综合教学楼，JA等"
            )

        full_message = "".join(message_parts)
        full_message = (
            f"[CQ:reply,id={message_id}]{full_message}\n\n"
            "当前数据依据ics后台提供,数据量匮乏,可能有大部分教室无法获取到,本功能只提供有考试的教室,且不能保证100%覆盖,仅供参考。\n"
            "如果你想提供你的考试数据,请前往 https://qfnuics.easy-qfnu.top 将你的考试数据导出ics,数据将会存在后台以供大家使用（整个过程完全匿名）。"
        )
        await send_group_msg(
            websocket,
            group_id,
            full_message,
        )


# 群消息处理函数
async def handle_QFNUBustExamClassroomFind_group_message(websocket, msg):
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

        authorized = user_id in owner_id

        # 开关
        if raw_message == "qfnubecf":
            await toggle_function_status(websocket, group_id, message_id, authorized)
            return

        # 检查是否开启
        if not load_function_status(group_id):
            return
        else:
            await process_exam_classroom_info(
                websocket, group_id, message_id, raw_message
            )

    except Exception as e:
        logging.error(f"处理QFNUBustExamClassroomFind群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌处理QFNUBustExamClassroomFind群消息失败,错误信息："
            + str(e),
        )
        return
