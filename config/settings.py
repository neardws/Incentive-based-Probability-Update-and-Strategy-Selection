#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   settings.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/28 下午1:53   neardws      1.0         None
"""

# MySQL and csv file
username = "root"
port = 3306
database = "vehicleCD"
csv_name = "./data/data.csv"
xy_csv_name = "./data/xy_data.csv"
fill_xy_csv_name = "./data/fill_xy.csv"
init_csv_name = "./data/init.csv"
task_csv_name = "./data/task.csv"

# SQL search condition
start_time = "2014-08-20 09:00:00"
stop_time = "2014-08-20 09:05:00"
time_length = 300

zone_length = 3000
base_latitude = 30.646166
base_longitude = 104.045824

channel_resource = 100
transmission_power = 40


"""##################################
#  Experiment  Settings
##################################"""

"""##################################
#  Edge Node  Settings
##################################"""
# 基站、RSU数量以及 子信道总数量
base_station_num = 2
rsu_num = 9
sub_channel_num = 100

# 基站位置
base_station_x = [800, 2000]
base_station_y = [800, 2000]

# RSU位置
rsu_x = [1000, 1500, 2500, 2500, 2500, 500, 1300, 500, 1700]
rsu_y = [1500, 500, 500, 1300, 2500, 2000, 2500, 2500, 1000]

# 通讯半径
base_station_communication_radius = 800
rsu_communication_radius = 500
edge_vehicle_communication_radius = 300

# 最大传输功率
base_station_transmission_power_max = 20
rsu_transmission_power_max = 5
edge_vehicle_transmission_power_max = 1

# 边缘节点信道数量
base_station_sub_channel_num = 80
rsu_sub_channel_num = 50
edge_vehicle_sub_channel_num = 30

# 子信道带宽 1MHz
sub_channel_bandwidth = 1000

"""##################################
#  Vehicular Transmission Task Settings
##################################"""
# 传输数据任务数据量向大小
task_data_size_min = 1
task_data_size_max = 10

# 传输数据任务截止时间
task_deadline_min = 1
task_deadline_max = 5

"""##################################
#  Wireless Communication Parameters Value Settings
##################################"""
# 信道衰落增益
channel_fading_gain_ex = 2
channel_fading_gain_dx = 0.4

# 无线相关常数
antenna_constant = 1

# 路径衰落指数
path_loss_exponent = 3

# 高斯白噪声
white_gaussian_noise = 10e-12

"""##################################
#  Algorithm Parameters Value Settings
##################################"""
# 学习率
learning_rate = 0.01
