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
import itertools
from tqdm import tqdm
import random


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


def init_useful_channel(node_type, node_id, fixed_edge_node, edge_vehicle_node):
    if node_type == settings.NODE_TYPE_BASE_STATION:
        node = fixed_edge_node[node_id]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == settings.NODE_TYPE_RSU:
        node = fixed_edge_node[node_id + settings.base_station_num]
        node_channel = node["sub_channel"]
        channel_status = np.zeros(len(node_channel))
        useful_channel = {"node_channel": node_channel, "channel_status": channel_status}
        return useful_channel
    elif node_type == settings.NODE_TYPE_VEHICLE:
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


def next_time_slot_useful_channel(useful_channel):
    # 下一个时间片，对其自减
    for i in range(len(useful_channel)):
        if useful_channel["channel_status"][i] != 0:
            useful_channel["channel_status"][i] -= 1


def get_usable_channel_list(useful_channel):
    """
    :argument
        useful_channel
    :return
        usable_channel_list     当前可用的信道
    """
    usable_channel_list = []

    channel_status = useful_channel["channel_status"]
    node_channel = useful_channel["node_channel"]
    for i in range(len(node_channel)):
        if channel_status[i] == 0:
            usable_channel_list.append(node_channel[i])

    return usable_channel_list


def get_combination_and_strategy_length(usable_channel_list_len, task_id_under_edge_node, time_limitation_under_edge_node):
    if len(task_id_under_edge_node) != 0:
        combination_of_task_and_time = [[-1, -1]]
        for i, task_id in enumerate(task_id_under_edge_node):
            for j in range(int(time_limitation_under_edge_node[i])):
                combination_of_task_and_time.append([task_id, j + 1])
        return {"combination_of_task_and_time": combination_of_task_and_time,
                "length_of_strategy_list": np.power(usable_channel_list_len, len(combination_of_task_and_time))}
    else:
        return


def decimal2xBase(decimal_num, x_base):
    x_base_num = []
    while True:
        quotient = decimal_num // x_base  # 商
        remainder = decimal_num % x_base  # 余数
        x_base_num = x_base_num + [remainder]
        if quotient == 0:
            break
        decimal_num = quotient
    x_base_num.reverse()
    return x_base_num


def constructor_of_strategy(x_base_num, combination_and_strategy_length):
    strategy = []
    combination = combination_and_strategy_length["combination_of_task_and_time"]
    for i in x_base_num:
        strategy.append(combination[i])
    return strategy


def generator_of_strategy_selection_probability(strategy_list_length):
    strategy_selection_probability = list(itertools.repeat(0.5, strategy_list_length))
    return strategy_selection_probability


def binary_search(sorted_list, start, end, x):
    if end >= start:
        middle = int(start + (end - start) / 2)
        if sorted_list[middle] < x:
            if sorted_list[middle + 1] > x:
                return middle + 1
            else:
                return binary_search(sorted_list, middle + 1, end, x)
        elif sorted_list[middle] > x:
            if sorted_list[middle - 1] < x:
                return middle
            else:
                return binary_search(sorted_list, start, middle - 1, x)
        else:
            return middle


def weighted_choice(strategy_selection_probability):
    random_num = random.random() * sum(strategy_selection_probability)
    return binary_search(list(itertools.accumulate(strategy_selection_probability)), 0, len(strategy_selection_probability) - 1, random_num)


def random_channel_fading_gain():
    channel_fading_gain = np.random.normal(settings.CHANNEL_FADING_GAIN_EX,
                                           settings.CHANNEL_FADING_GAIN_DX,
                                           1)
    return channel_fading_gain


def compute_signal_list(channel,
                        task_id,
                        fixed_node,
                        mobile_node,
                        useful_channel_list_under_fixed_node,
                        useful_channel_list_under_mobile_node,
                        fixed_distance_matrix,
                        mobile_distance_matrix):
    signal_list = []

    antenna_constant = settings.ANTENNA_CONSTANT
    path_loss_exponent = settings.PATH_LOSS_EXPONENT

    for node_no, useful_channel in enumerate(useful_channel_list_under_fixed_node):
        node_channel = useful_channel["node_channel"]
        channel_status = useful_channel["channel_status"]
        for i, channel_no in enumerate(node_channel):
            if channel_no == channel:
                if channel_status[i] > 0:
                    distance = fixed_distance_matrix[node_no][task_id]
                    channel_fading_gain = random_channel_fading_gain()
                    transmission_power = fixed_node[node_no]["channel_power"]
                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(distance,
                                                                                                0 - path_loss_exponent) * transmission_power
                    signal = {"node_type": settings.NODE_TYPE_FIXED,
                              "node_id": node_no,
                              "signal": signal_value}
                    signal_list.append(signal)

    for node_no, useful_channel in enumerate(useful_channel_list_under_mobile_node):
        node_channel = useful_channel["node_channel"]
        channel_status = useful_channel["channel_status"]
        for i, channel_no in enumerate(node_channel):
            if channel_no == channel:
                if channel_status[i] > 0:
                    distance = mobile_distance_matrix[node_no][task_id]
                    channel_fading_gain = random_channel_fading_gain()
                    transmission_power = mobile_node[node_no]["channel_power"]
                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(distance,
                                                                                                0 - path_loss_exponent) * transmission_power
                    signal = {"node_type": settings.NODE_TYPE_MOBILE,
                              "node_id": node_no,
                              "signal": signal_value}
                    signal_list.append(signal)

    return signal_list


def compute_SINR(node_type,
                 node_no,
                 channel,
                 task_id,
                 fixed_node,
                 mobile_node,
                 useful_channel_list_under_fixed_node,
                 useful_channel_list_under_mobile_node,
                 fixed_distance_matrix,
                 mobile_distance_matrix):
    SINR = 0

    white_gaussian_noise = settings.WHITE_GAUSSIAN_NOISE

    signal = 0
    interference = 0

    signal_list = compute_signal_list(channel=channel,
                                      task_id=task_id,
                                      fixed_node=fixed_node,
                                      mobile_node=mobile_node,
                                      useful_channel_list_under_fixed_node=useful_channel_list_under_fixed_node,
                                      useful_channel_list_under_mobile_node=useful_channel_list_under_mobile_node,
                                      fixed_distance_matrix=fixed_distance_matrix,
                                      mobile_distance_matrix=mobile_distance_matrix)
    for signal_dict in signal_list:
        if signal_dict["node_type"] == node_type:
            if signal_dict["node_no"] == node_no:
                signal = signal_dict["signal"]
            else:
                interference += signal_dict["signal"]
        else:
            interference += signal_dict["signal"]

    SINR = signal / (interference + white_gaussian_noise)

    return SINR


def compute_task_transmission_data(task_id_list,
                                   strategy,
                                   node_type,
                                   node_no,
                                   fixed_node,
                                   mobile_node,
                                   useful_channel_list_under_fixed_node,
                                   useful_channel_list_under_mobile_node,
                                   fixed_distance_matrix,
                                   mobile_distance_matrix):
    sub_channel_bandwidth = settings.SUB_CHANNEL_BANDWIDTH

    task_transmission_data_list = []
    for task_id in task_id_list:
        task_data_size = 0
        [x, y] = strategy.shape
        for channel_no in range(x):
            if task_id == strategy[channel_no][0]:
                task_time = strategy[channel_no][1]
                SINR = compute_SINR(node_type=node_type,
                                    node_no=node_no,
                                    channel=channel_no,
                                    task_id=task_id,
                                    fixed_node=fixed_node,
                                    mobile_node=mobile_node,
                                    useful_channel_list_under_fixed_node=useful_channel_list_under_fixed_node,
                                    useful_channel_list_under_mobile_node=useful_channel_list_under_mobile_node,
                                    fixed_distance_matrix=fixed_distance_matrix,
                                    mobile_distance_matrix=mobile_distance_matrix)
                channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                task_data_size += channel_data_size
        task_transmission_data = {"task_id": task_id,
                                  "task_data_size": task_data_size}
        task_transmission_data_list.append(task_transmission_data)

    return task_transmission_data_list


def compute_task_is_finished(task_list, task_transmission_data_list_of_all_nodes):
    finished = np.zeros(len(task_list))

    task_size = np.zeros(len(task_list))

    for task_transmission_data_list in task_transmission_data_list_of_all_nodes:
        for task_transmission_data in task_transmission_data_list:
            task_id = task_transmission_data["task_id"]
            task_data_size = task_transmission_data["task_data_size"]
            task_size[task_id] += task_data_size

    for i, size in enumerate(task_size):
        task_need_size = task_list[i]["task_size"]
        if size >= task_need_size * 8 * 1024 * 1024:
            finished[i] = 1

    return finished


def compute_potential_value(task_id_list_under_edge_node, finished):
    potential_value = 0
    for task_id in task_id_list_under_edge_node:
        if finished[task_id] == 1:
            potential_value += 1
    return potential_value


def compute_probability_update_value(potential_value, max_potential_value):
    probability_update_value = (potential_value - max_potential_value) / max_potential_value
    return probability_update_value


def compute_updated_probability(origin_probability, learning_rate, probability_update_value):
    if probability_update_value >= 0:
        new_probability = origin_probability + (1 - origin_probability) * learning_rate * probability_update_value
        return new_probability
    else:
        new_probability = origin_probability - origin_probability * learning_rate * probability_update_value
        return new_probability


if __name__ == '__main__':
    # generator_of_strategy_list(usable_channel_list_len=10,
    #                            task_id_under_edge_node_len=4,
    #                            task_time_limitation_under_edge_node=[1,2,1,1])
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # generator_of_strategy_selection_probability(1000000000)
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # # print(generator_of_strategy_selection_probability(100000000))
    # # read_experiment()
    # # print(random_channel_fading_gain())
    # # print("*" * 32)
    # # noise = settings.WHITE_GAUSSIAN_NOISE
    # # print(noise)
    # # print(type(noise))
    # x_length = 5
    # y_length = 4
    # task_time_limitation_under_edge_node = [1, 2, 1, 1]
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # strategy_list = generator_of_strategy_list(10, 4, task_time_limitation_under_edge_node)
    # print(strategy_list[1])
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # exit()
    # # # print(len(strategy_list))
    # combination_of_task_and_time = get_combination_of_task_and_time(10, task_id_under_edge_node=[4, 8, 16, 19],
    #                                                                 time_limitation_under_edge_node=[2, 2, 1, 2])
    # print(combination_of_task_and_time)
    # probability_list = generator_of_strategy_selection_probability(combination_of_task_and_time["length_of_strategy_list"])
    # choose = weighted_choice(probability_list)
    # decimal2xBase(choose, len(combination_of_task_and_time["combination_of_task_and_time"]))
    print(np.power(10, 10))
