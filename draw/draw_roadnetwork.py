# %%
import matplotlib.pyplot as plt  # 导入绘图模块
import numpy as np  #  导入需要生成数据的numpy模块
from config import settings
import numpy as np
import pandas as pd
import random
# get_ipython().run_line_magic("matplotlib", "widget")


# %%
# -------------------------------------------------区域坐标---------------------------------------------
bottom_lat = 30.646166
top_lat = 30.67345959539793
left_lng = 104.045824
right_lng = 104.07687225084355
# ------------------------------------------------------------------------------------------------------

# -------------------------------------------------绘图部分----------------------------------------------
# 数据设定
# plt.xlim(0,3000)   # 设置x轴的刻度从-2到12
# plt.ylim(0,3000)
# 设定背景图片
bgimg = plt.imread("roadNetwork.png")
# 获取图片大小作为画布大小
width, height = bgimg.shape[:2]
dpi = 100
fig = plt.figure(1, (width / dpi, height / dpi), dpi=100)
# 子区域大小
rect = [0, 0, 1, 1]
# 第一个子区域
axes0 = fig.add_axes(rect, label="axes0")
axes0.set_axis_off()
axes0.imshow(bgimg, alpha=0.55)
# 第二个子区域
axes1 = fig.add_axes(rect, label="axes1")
axes1.set_axis_off()
# axes1.ylim(0, 3000)
# axes1.xlim(0, 3000)
axes1.set_ylim(0, 3000)
axes1.set_xlim(0, 3000)
x = y = np.arange(0, 3000, 1)
x, y = np.meshgrid(x, y)
# 基站：2个
basestation_x = [700, 2000]
basestation_y = [700, 2000]
radius_big = 700
# Rsu:9个
rsu_x = [1000, 1500, 2500, 2500, 2500, 500, 1300, 500, 1700]
rsu_y = [1500, 500, 500, 1300, 2500, 2000, 2500, 2500, 1000]
radius_small = 500


for x_cord, y_cord in zip(basestation_x, basestation_y):
    axes1.add_patch(plt.Circle((x_cord, y_cord), radius_big, color="#000000", fill=False, linestyle="--"))
    axes1.scatter(x_cord, y_cord, marker="^", color="#000000")


for x_cord, y_cord in zip(rsu_x, rsu_y):
    axes1.add_patch(plt.Circle((x_cord, y_cord), radius_small, color="blue", fill=False, linestyle="--"))
    axes1.scatter(x_cord, y_cord, marker="o", color="blue")

df = pd.read_csv(settings.TASK_CSV_NAME)
df = df[df["time"] == 1]
task_x = df["x"].tolist()
task_y = df["y"].tolist()
for i in range(len(task_x)):
    random_value = random.random()
    print(random_value)
    if random_value <= 0.95:
        print(True)
        plt.plot(int(task_x[i]+30), int(task_y[i]), color="red", marker=".", markersize=3)
    else:
        print(False)
        axes1.add_patch(plt.Circle((int(task_x[i]+30), int(task_y[i])), 300, color="green", fill=False, linestyle="--"))
        axes1.scatter(int(task_x[i]+30), int(task_y[i]), marker="+", color="green")

plt.show()
# ------------------------------------------------------------------------------------------------------------

