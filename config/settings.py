#!./venv python
# -*- encoding: utf-8 -*-
"""
@file    :   settings.py
@contact :   neard.ws@gmail.com
@github  :   neardws

@modify time      @author    @version    @desciption
------------      -------    --------    -----------
2020/8/28 下午1:53   neardws      1.0         none
"""

# mysql and csv file
USERNAME = "root"
PORT = 3306
DATABASE = "vehiclecd"
CSV_NAME = "../data/data.csv"
XY_CSV_NAME = "../data/xy_data.csv"
FILL_XY_CSV_NAME = "../data/fill_xy.csv"
INIT_CSV_NAME = "../data/init.csv"
TASK_CSV_NAME = "../data/task.csv"

# sql search condition
START_TIME = "2014-08-20 09:00:00"
STOP_TIME = "2014-08-20 09:05:00"
TIME_LENGTH = 300

ZONE_LENGTH = 3000
BASE_LATITUDE = 30.646166
BASE_LONGITUDE = 104.045824

CHANNEL_RESOURCE = 100
TRANSMISSION_POWER = 40

"""##################################
#  experiment  settings
##################################"""

"""##################################
#  edge node  settings
##################################"""
# 基站、rsu数量以及 子信道总数量
BASE_STATION_NUM = 2
RSU_NUM = 9
EDGE_VEHICLE_NUM = 7
SUB_CHANNEL_NUM = 10

# 基站位置
BASE_STATION_X = [700, 2000]
BASE_STATION_Y = [700, 2000]

# rsu位置
RSU_X = [1000, 1500, 2500, 2500, 2500, 500, 1300, 500, 1700]
RSU_Y = [1500, 500, 500, 1300, 2500, 2000, 2500, 2500, 1000]

# 通讯半径
BASE_STATION_COMMUNICATION_RADIUS = 700
RSU_COMMUNICATION_RADIUS = 500
EDGE_VEHICLE_COMMUNICATION_RADIUS = 300

# 最大传输功率
BASE_STATION_TRANSMISSION_POWER_MAX = 20
RSU_TRANSMISSION_POWER_MAX = 5
EDGE_VEHICLE_TRANSMISSION_POWER_MAX = 1

# 边缘节点信道数量
BASE_STATION_SUB_CHANNEL_NUM = 10
RSU_SUB_CHANNEL_NUM = 10
EDGE_VEHICLE_SUB_CHANNEL_NUM = 10

# 子信道带宽 50Khz = 5*10^4 Hz
SUB_CHANNEL_BANDWIDTH = 5e4

"""##################################
#  vehicular transmission task settings
##################################"""
# 传输数据任务数据量向大小, 单位Mb
TASK_DATA_SIZE_MIN = 1
TASK_DATA_SIZE_MAX = 1

# 传输数据任务截止时间
TASK_DEADLINE_MIN = 1
TASK_DEADLINE_MAX = 1

"""##################################
#  wireless communication parameters value settings
##################################"""
# 信道衰落增益
CHANNEL_FADING_GAIN_EX = 2
CHANNEL_FADING_GAIN_DX = 0.4

# 无线相关常数
ANTENNA_CONSTANT = 1

# 路径衰落指数
PATH_LOSS_EXPONENT = 3

# 高斯白噪声
WHITE_GAUSSIAN_NOISE = 10e-12

"""##################################
#  algorithm parameters value settings
##################################"""
# 学习率
LEARNING_RATE = 10

"""##################################
#  experiment parameters value settings
##################################"""
# 实验开始时间
EXPERIMENT_START_TIME = 1

# 实验持续时间
EXPERIMENT_LAST_TIME = 10

EXPERIMENT_FILE_NAME = "../experiment_data/experiment_file_name.txt"
EXPERIMENT_MEDIAN_FILE_NAME = "../experiment_data/experiment_median_file_name.txt"
ITERATION_MEDIAN_FILE_NAME = "../experiment_data/iteration_median_file_name.txt"
H5PY_FILE = "../experiment_data/strategy_selection_probability_of_all_node.hdf5"
JSON_FILE = "../experiment_data/experiment_output/iteration_results.json"

JSON_FILE_VER2 = "../experiment_data/experiment_output/iteration_results_ver2.json"
JSON_FILE_VER3 = "../experiment_data/experiment_output/iteration_results_ver3.json"

JSON_FILE_VER2_9 = "../experiment_data/experiment_output/iteration_results_ver3_9.json"
JSON_FILE_VER2_10 = "../experiment_data/experiment_output/iteration_results_ver3_10.json"
JSON_FILE_VER2_11 = "../experiment_data/experiment_output/iteration_results_ver3_11.json"
JSON_FILE_VER2_12 = "../experiment_data/experiment_output/iteration_results_ver3_12.json"
JSON_FILE_VER2_13 = "../experiment_data/experiment_output/iteration_results_ver3_13.json"
JSON_FILE_VER2_14 = "../experiment_data/experiment_output/iteration_results_ver3_14.json"
JSON_FILE_VER2_15 = "../experiment_data/experiment_output/iteration_results_ver3_15.json"
JSON_FILE_VER2_16 = "../experiment_data/experiment_output/iteration_results_ver3_16.json"
JSON_FILE_VER2_17 = "../experiment_data/experiment_output/iteration_results_ver3_17.json"
JSON_FILE_VER2_18 = "../experiment_data/experiment_output/iteration_results_ver3_18.json"

RESULT_FILE_VER2_9 = "../experiment_data/experiment_output/iteration_only_results_ver3_9.json"
RESULT_FILE_VER2_10 = "../experiment_data/experiment_output/iteration_only_results_ver3_10.json"
RESULT_FILE_VER2_11 = "../experiment_data/experiment_output/iteration_only_results_ver3_11.json"
RESULT_FILE_VER2_12 = "../experiment_data/experiment_output/iteration_only_results_ver3_12.json"
RESULT_FILE_VER2_13 = "../experiment_data/experiment_output/iteration_only_results_ver3_13.json"
RESULT_FILE_VER2_14 = "../experiment_data/experiment_output/iteration_only_results_ver3_14.json"
RESULT_FILE_VER2_15 = "../experiment_data/experiment_output/iteration_only_results_ver3_15.json"
RESULT_FILE_VER2_16 = "../experiment_data/experiment_output/iteration_only_results_ver3_16.json"
RESULT_FILE_VER2_17 = "../experiment_data/experiment_output/iteration_only_results_ver3_17.json"
RESULT_FILE_VER2_18 = "../experiment_data/experiment_output/iteration_only_results_ver3_18.json"

# 边缘节点的类型
NODE_TYPE_BASE_STATION = "BaseStation"
NODE_TYPE_RSU = "RSU"
NODE_TYPE_VEHICLE = "Vehicle"

NODE_TYPE_FIXED = "Fixed_Edge_Node"
NODE_TYPE_MOBILE = "Mobile_Edge_Node"

