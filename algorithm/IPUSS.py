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
import math
from datetime import *
import numpy as np
from config.config import settings
import itertools
import random


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
    for i in range(len(strategy)):
        if strategy[i][0] != 0 and strategy[i][0] != -1:
            channel_time = strategy[i][1]
            useful_channel["channel_status"][i] = channel_time
    return useful_channel


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
        length_of_combination = int(len(combination_of_task_and_time)),
        return {"combination_of_task_and_time": combination_of_task_and_time,
                "length_of_combination": length_of_combination,
                "length_of_strategy_list": np.power(length_of_combination, usable_channel_list_len)}
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


def constructor_of_strategy(x_base_num, combination):
    strategy = []
    for i in x_base_num:
        strategy.append(combination[i])
    return strategy


def weighted_choice(strategy_list_length, probabilities_wight_dict):
    # 得到随机数
    if probabilities_wight_dict:
        weight_sum = strategy_list_length

        for key in probabilities_wight_dict.keys():
            weight_sum = weight_sum - 1 + probabilities_wight_dict[key]

        random_num = random.random() * weight_sum
        # 根据 probabilities_wight_dict 中的值进行查询
        # probabilities_wight_dict 是已根据序号 i 排好序的
        added_sum = 0
        now_no = 0
        for key in sorted(probabilities_wight_dict):
            strategy_no = int(key)
            strategy_weight = probabilities_wight_dict[key]
            compare_number = random_num - added_sum
            if strategy_weight >= 1:
                compare_number -= (strategy_weight - 1)
            if compare_number <= strategy_no - now_no:
                return math.floor(compare_number) + now_no
            added_sum += strategy_no - 1 + strategy_weight - now_no
            now_no = strategy_no
        compare_number = random_num - added_sum
        return math.floor(compare_number) + now_no
    else:
        weight_sum = strategy_list_length
        random_num = random.random() * weight_sum
        return math.floor(random_num)


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
                              "node_id": node_no + int(len(fixed_node)),
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
            if signal_dict["node_id"] == node_no:
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
        x = len(strategy)
        # print(strategy)
        # print(type(strategy))
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


def compute_task_is_finished(task_list, task_transmission_data_dict_of_all_nodes):
    finished = np.zeros(len(task_list))

    task_size = np.zeros(len(task_list))

    for key in task_transmission_data_dict_of_all_nodes.keys():
        task_transmission_data_list = task_transmission_data_dict_of_all_nodes[key]

        for task_transmission_data in task_transmission_data_list:
            task_id = task_transmission_data["task_id"]
            task_data_size = task_transmission_data["task_data_size"]
            task_size[task_id] += task_data_size

    for i, size in enumerate(task_size):
        task_need_size = task_list[i]["data_size"]
        if size >= task_need_size * 1024 * 1024:
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
    if probability_update_value > 0:
        learning_rate = 1000
        new_probability = origin_probability * learning_rate * probability_update_value
        return new_probability
    elif probability_update_value == 0:
        return origin_probability
    else:
        new_probability = origin_probability / (learning_rate * (- probability_update_value))
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
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # np_array2 = generator_of_strategy_selection_probability2(np.power(10, 10))
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    np_array1 = generator_of_strategy_selection_probability(np.power(6, 10))
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    i = weighted_choice(np_array1)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("")
