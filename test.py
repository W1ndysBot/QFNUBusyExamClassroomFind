from datetime import datetime
print(datetime.now())
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间，精确到秒
print(current_time)
