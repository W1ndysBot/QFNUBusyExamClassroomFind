# script/QFNUBustExamClassroomFind/main.py

import logging
import os
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
)

# 数据存储路径，实际开发时，请将QFNUBustExamClassroomFind替换为具体的数据存放路径
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

        authorized = is_authorized(role, user_id)

        # 开关
        if raw_message == "qfnubecf":
            # 检查开关
            if not authorized:
                await send_group_msg(
                    websocket,
                    group_id,
                    f"[CQ:reply,id={message_id}]❌❌❌你没有权限使用此功能，请联系管理员。",
                )
                return
            else:
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
                        f"[CQ:reply,id={message_id}]✅✅✅曲阜师范大学期末考试考场教室查询功能已开启",
                    )

        # 检查是否开启
        if not load_function_status(group_id):
            return
        else:
            match = re.match(r"(.*)考场", raw_message)
            if match:
                building_name = match.group(1)
                query_classrooms(building_name)

    except Exception as e:
        logging.error(f"处理QFNUBustExamClassroomFind群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌处理QFNUBustExamClassroomFind群消息失败，错误信息："
            + str(e),
        )
        return
