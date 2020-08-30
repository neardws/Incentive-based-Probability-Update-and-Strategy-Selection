#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   IPUSS.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 下午5:11   neardws      1.0         None
"""
from datetime import *
from init_input.experiment_input_save_and_reload import load_pickle
from pathlib import Path
import pickle
import numpy as np
from init_input.init_distance import get_task_time_limitation_under_edge_node, get_task_id_under_edge_node
from config.config import settings
from itertools import accumulate, repeat, product
from tqdm import tqdm
import random


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


def read_experiment():
    pickle_file = Path(load_pickle(4))
    with pickle_file.open("rb") as fp:
        fixed_edge_node = pickle.load(fp)
        print_to_console("fixed_edge_node", fixed_edge_node)

        edge_vehicle_node = pickle.load(fp)
        print_to_console("edge_vehicle_node", edge_vehicle_node)

        task_by_time_list = pickle.load(fp)
        print_to_console("task_by_time_list", task_by_time_list)

        fixed_distance_matrix_list = pickle.load(fp)
        print_to_console("fixed_distance_matrix_list", fixed_distance_matrix_list)

        mobile_distance_matrix_list = pickle.load(fp)
        print_to_console("mobile_distance_matrix_list", mobile_distance_matrix_list)

        task_id = get_task_id_under_edge_node(node_type="BaseStation",
                                              node_id=1,
                                              distance_matrix=fixed_distance_matrix_list[0])
        print_to_console("task_id", task_id)


        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(node_type="BaseStation",
                                                                                        node_id=1,
                                                                                        distance_matrix_list=fixed_distance_matrix_list,
                                                                                        task_list=task_by_time_list[0])

        print_to_console("task_time_limitation_under_edge_node", task_time_limitation_under_edge_node)


def init_useful_channel(node_type, node_id, fixed_edge_node, edge_vehicle_node):
    if node_type == "BaseStation":
        node = fixed_edge_node[node_id]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel":node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == "RSU":
        node = fixed_edge_node[node_id + settings.base_station_num]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == "Vehicle":
        node = edge_vehicle_node[node_id]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    else:
        raise ValueError("from IPUSS.init_userful_channel 节点类型出错， 不是指定类型")


def update_useful_channel(strategy, useful_channel):
    for i in range(len(useful_channel)):
        if strategy[i][0] != 0:
            channel_time = strategy[i][1]
            useful_channel["channel_status"][i] = channel_time


def get_usable_channel_list(useful_channel):
    # 下一个时间片，对其自减
    for i in range(len(useful_channel)):
        if useful_channel["channel_status"][i] != 0:
            useful_channel["channel_status"][i] -= 1

    usable_channel_list = []

    channel_status = useful_channel["channel_status"]
    node_channel = useful_channel["node_channel"]
    for i in range(len(useful_channel)):
        if channel_status[i] == 0:
            usable_channel_list.append(node_channel[i])

    return usable_channel_list


def generator_of_strategy_list(usable_channel_list, task_id_under_edge_node, task_time_limitation_under_edge_node):

    # x 轴，节点当前可用的信道
    x_length = len(usable_channel_list)

    # y 轴, 节点的所有任务数
    # task_id = get_task_id_under_edge_node(node_type=node_type,
    #                                       node_id=node_id,
    #                                       distance_matrix=distance_matrix_list[time])
    y_length = len(task_id_under_edge_node)

    # task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(node_type="BaseStation",
    #                                                                                 node_id=1,
    #                                                                                 distance_matrix_list=distance_matrix_list,
    #                                                                                 task_list=task_by_time_list[
    #                                                                                     time - 1])
    j_strategy_list = [np.zeros(2)]

    for j in range(y_length):
        for k in range(task_time_limitation_under_edge_node[j]):
            j_strategy = np.zeros(2)
            j_strategy[0] = j + 1
            j_strategy[1] = k + 1
            j_strategy_list.append(j_strategy)
    print(j_strategy_list)
    print(len(j_strategy_list))

    strategy_list = []
    for strategy in product(j_strategy_list, repeat=x_length):
        strategy_list.append(strategy)

    return strategy_list


def generator_of_strategy_selection_probability(strategy_list_length):
    strategy_selection_probability = list(repeat("0.5", strategy_list_length))
    return strategy_selection_probability


def weighted_choice(strategy_selection_probability):
    random_num = random.random() * sum(strategy_selection_probability)
    for i, weight_sum in enumerate(list(accumulate(strategy_selection_probability))):
        if random_num < weight_sum:
            return i


def random_channel_fading_gain():
    channel_fading_gain = np.random.normal(settings.CHANNEL_FADING_GAIN_EX,
                                           settings.CHANNEL_FADING_GAIN_DX,
                                           1)
    return channel_fading_gain


def compute_SINR(channel, task_id, strategy, other_node_strategy_list, distance):
    SINR = 0

    noise = settings.WHITE_GAUSSIAN_NOISE
    numerator = np.square(random_channel_fading_gain()) * settings.ANTENNA_CONSTANT * np.power(distance, 0 - settings.PATH_LOSS_EXPONENT)

    denominator = 0 # TODO

    return SINR


def compute_signal_list(channel,
                        task_id,
                        fixed_node,
                        mobile_node,
                        usable_channel_list_under_fixed_node,
                        usable_channel_list_under_mobile_node,
                        fixed_distance_matrix,
                        mobile_distance_matrix):
    signal_list = []

    antenna_constant = settings.ANTENNA_CONSTANT
    path_loss_exponent = settings.PATH_LOSS_EXPONENT

    for node_no, usable_channel in enumerate(usable_channel_list_under_fixed_node):
        node_channel = usable_channel["node_channel"]
        channel_status = usable_channel["channel_status"]
        for i, channel_no in enumerate(node_channel):
            if channel_no == channel:
                if channel_status[i] > 0:
                    distance = fixed_distance_matrix[node_no][task_id]
                    channel_fading_gain = random_channel_fading_gain()
                    transmission_power = fixed_node[node_no]["channel_power"]
                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(distance, 0 - path_loss_exponent) * transmission_power
                    signal = {"node_type": settings.NODE_TYPE_FIXED,
                              "node_id": node_no,
                              "signal": signal_value}
                    signal_list.append(signal)

    for node_no, usable_channel in enumerate(usable_channel_list_under_mobile_node):
        node_channel = usable_channel["node_channel"]
        channel_status = usable_channel["channel_status"]
        for i, channel_no in enumerate(node_channel):
            if channel_no == channel:
                if channel_status[i] > 0:
                    distance = mobile_distance_matrix[node_no][task_id]
                    channel_fading_gain = random_channel_fading_gain()
                    transmission_power = mobile_node[node_no]["channel_power"]
                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(distance, 0 - path_loss_exponent) * transmission_power
                    signal = {"node_type": settings.NODE_TYPE_MOBILE,
                              "node_id": node_no,
                              "signal": signal_value}
                    signal_list.append(signal)

    return signal_list


def compute_task_transmission_data(task_id_list, strategy):
    for task_id in task_id_list:
        [x, y] = strategy.shape
        for i in range(x):
            if task_id == strategy[i][0]:
                task_time = strategy[i][1]

    pass


# def get_strategy(x_length, y_length, task_time_limitation_under_edge_node):
#     strategy_list = []
#
#     j_strategy_list = [np.zeros(2)]
#
#     for j in tqdm(range(y_length)):
#         for k in range(task_time_limitation_under_edge_node[j]):
#             j_strategy = np.zeros(2)
#             j_strategy[0] = j + 1
#             j_strategy[1] = k + 1
#             j_strategy_list.append(j_strategy)
#     print(j_strategy_list)
#     print(len(j_strategy_list))
#
#     for strategy in tqdm(itertools.product(j_strategy_list, repeat=x_length)):
#         strategy_list.append(strategy)
#
#     return strategy_list

if __name__ == '__main__':
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # generator_of_strategy_selection_probability(1000000000)
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # print(generator_of_strategy_selection_probability(100000000))
    # read_experiment()
    print(random_channel_fading_gain())
    print("*" * 32)
    noise = settings.WHITE_GAUSSIAN_NOISE
    print(noise)
    print(type(noise))
    # x_length = 5
    # y_length = 4
    # task_time_limitation_under_edge_node = [3, 2, 6, 2]
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # strategy_list = get_strategy(5, 4, task_time_limitation_under_edge_node)
    # print(strategy_list[1])
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # print(len(strategy_list))
