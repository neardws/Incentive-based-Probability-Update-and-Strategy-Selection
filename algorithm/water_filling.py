#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   water_filling.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 下午5:11   neardws      1.0         None
"""
import random

import numpy as np
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS_ver2 import update_useful_channel, random_channel_fading_gain
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from .random_selection import random_selection_strategy


def water_filling_selection(combinations_in_list, length, experiment_median_num, node_num):
    strategy_list = random_selection_strategy(combinations_in_list, length)
    new_strategy_list = judge_SINR(strategy_list=strategy_list,
                                   SINR_threshold=3,
                                   experiment_median_num=experiment_median_num,
                                   node_num=node_num,
                                   combinations_in_list=combinations_in_list)
    return new_strategy_list


def judge_SINR(strategy_list, SINR_threshold, experiment_median_num, node_num, combinations_in_list):
    pickle_file = Path(load_experiment_median_from_pickle(experiment_median_num))
    fp = pickle_file.open("rb")
    iteration = pickle.load(fp)
    fixed_edge_node = pickle.load(fp)
    edge_vehicle_node = pickle.load(fp)
    fixed_distance_matrix = pickle.load(fp)
    mobile_distance_matrix = pickle.load(fp)
    task_list = pickle.load(fp)
    node_num_not_used = pickle.load(fp)
    fixed_node_num = pickle.load(fp)
    mobile_node_num = pickle.load(fp)
    max_potential_value = pickle.load(fp)
    useful_channel_under_node = pickle.load(fp)
    task_id_under_each_node_list = pickle.load(fp)
    usable_channel_of_all_nodes = pickle.load(fp)
    task_time_limitation_of_all_nodes = pickle.load(fp)
    combination_and_strategy_length_of_all_nodes = pickle.load(fp)



    union_task_id_set = set()
    for task_id_under_each_node in task_id_under_each_node_list:
        task_id_set = set(task_id_under_each_node)
        union_task_id_set = union_task_id_set | task_id_set

    white_gaussian_noise = settings.WHITE_GAUSSIAN_NOISE
    antenna_constant = settings.ANTENNA_CONSTANT
    path_loss_exponent = settings.PATH_LOSS_EXPONENT

    selected_strategy = dict()
    """
    ————————————————————————————————————————————————————————————————————————————————————
         选择策略
    ———————————————————————————————————————————————————————————————————————————————————— 
    """
    new_strategy_list = strategy_list

    for i, strategy in enumerate(strategy_list):
        selected_strategy[str(i)] = strategy

    # 更新信道分配
    for i in range(len(selected_strategy)):
        useful_channel_under_node[i] = update_useful_channel(selected_strategy[str(i)],
                                                             useful_channel_under_node[i])

    """
    ________________________________________________________________________________________________________________________________________-
                计算SINR
    *****************************************************************************************************************************************
    """
    node_type = settings.NODE_TYPE_FIXED
    for fixed_node_id in range(fixed_node_num):

        task_id_list = task_id_under_each_node_list[fixed_node_id]
        node_strategy = selected_strategy[str(fixed_node_id)]

        for task_id in task_id_list:

            for node_strategy_no in range(len(node_strategy)):  # 对于节点的每个信道上的分配
                allocated_channel_no = useful_channel_under_node[fixed_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号
                if task_id == node_strategy[node_strategy_no][0]:  # 为这个任务分配了信道

                    signal_list = list()  # 保存每个边缘节点使用相同信道时传输到任务上的信号

                    for node_no, useful_channel in enumerate(useful_channel_under_node[:fixed_node_num]):

                        node_channel = useful_channel["node_channel"]
                        channel_status = useful_channel["channel_status"]

                        for i, channel_no in enumerate(node_channel):
                            if allocated_channel_no == channel_no:
                                if channel_status[i] > 0:
                                    distance = fixed_distance_matrix[node_no][task_id]
                                    channel_fading_gain = random_channel_fading_gain()
                                    transmission_power = fixed_edge_node[node_no]["channel_power"]
                                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(
                                        distance,
                                        0 - path_loss_exponent) * transmission_power
                                    signal = {"node_type": settings.NODE_TYPE_FIXED,
                                              "node_id": node_no,
                                              "signal": signal_value[0]}
                                    signal_list.append(signal)

                    for node_no, useful_channel in enumerate(useful_channel_under_node[fixed_node_num:]):

                        node_channel = useful_channel["node_channel"]
                        channel_status = useful_channel["channel_status"]

                        for i, channel_no in enumerate(node_channel):
                            if allocated_channel_no == channel_no:
                                if channel_status[i] > 0:
                                    distance = mobile_distance_matrix[node_no][task_id]
                                    channel_fading_gain = random_channel_fading_gain()
                                    transmission_power = edge_vehicle_node[node_no]["channel_power"]
                                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(
                                        distance,
                                        0 - path_loss_exponent) * transmission_power
                                    signal = {"node_type": settings.NODE_TYPE_MOBILE,
                                              "node_id": node_no + int(len(fixed_edge_node)),
                                              "signal": signal_value}
                                    signal_list.append(signal)

                    inter_signal_value = 0
                    interference = 0

                    for signal_dict in signal_list:
                        if signal_dict["node_type"] == node_type:
                            if signal_dict["node_id"] == fixed_node_id:
                                inter_signal_value = signal_dict["signal"]
                            else:
                                interference += signal_dict["signal"]
                        else:
                            interference += signal_dict["signal"]

                    SINR = inter_signal_value / (interference + white_gaussian_noise)
                    if SINR < SINR_threshold:
                        random_num = random.randint(0, len(combinations_in_list[fixed_node_id]) - 1)
                        new_strategy_list[fixed_node_id][node_strategy_no] = \
                            combinations_in_list[fixed_node_id][random_num]


    node_type = settings.NODE_TYPE_MOBILE
    for mobile_node_id in range(fixed_node_num, node_num):

        task_id_list = task_id_under_each_node_list[mobile_node_id]
        node_strategy = selected_strategy[str(mobile_node_id)]

        for task_id in task_id_list:

            for node_strategy_no in range(len(node_strategy)):

                allocated_channel_no = useful_channel_under_node[mobile_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号

                if task_id == node_strategy[node_strategy_no][0]:

                    signal_list = list()

                    for node_no, useful_channel in enumerate(useful_channel_under_node[:fixed_node_num]):

                        node_channel = useful_channel["node_channel"]
                        channel_status = useful_channel["channel_status"]

                        for i, channel_no in enumerate(node_channel):
                            if allocated_channel_no == channel_no:
                                if channel_status[i] > 0:
                                    distance = fixed_distance_matrix[node_no][task_id]
                                    channel_fading_gain = random_channel_fading_gain()
                                    transmission_power = fixed_edge_node[node_no]["channel_power"]
                                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(
                                        distance,
                                        0 - path_loss_exponent) * transmission_power
                                    signal = {"node_type": settings.NODE_TYPE_FIXED,
                                              "node_id": node_no,
                                              "signal": signal_value}
                                    signal_list.append(signal)

                    for node_no, useful_channel in enumerate(useful_channel_under_node[fixed_node_num:]):

                        node_channel = useful_channel["node_channel"]
                        channel_status = useful_channel["channel_status"]

                        for i, channel_no in enumerate(node_channel):
                            if allocated_channel_no == channel_no:
                                if channel_status[i] > 0:
                                    distance = mobile_distance_matrix[node_no][task_id]
                                    channel_fading_gain = random_channel_fading_gain()
                                    transmission_power = edge_vehicle_node[node_no]["channel_power"]
                                    signal_value = np.square(channel_fading_gain) * antenna_constant * np.power(
                                        distance,
                                        0 - path_loss_exponent) * transmission_power
                                    signal = {"node_type": settings.NODE_TYPE_MOBILE,
                                              "node_id": node_no + int(len(fixed_edge_node)),
                                              "signal": signal_value}
                                    signal_list.append(signal)

                    inter_signal_value = 0
                    interference = 0

                    for signal_dict in signal_list:

                        if signal_dict["node_type"] == node_type:
                            if signal_dict["node_id"] == mobile_node_id:
                                inter_signal_value = signal_dict["signal"]
                            else:
                                interference += signal_dict["signal"]
                        else:
                            interference += signal_dict["signal"]

                    SINR = inter_signal_value / (interference + white_gaussian_noise)
                    if SINR < SINR_threshold:
                        random_num = random.randint(0, len(combinations_in_list[mobile_node_id]) - 1)
                        new_strategy_list[mobile_node_id][node_strategy_no] = \
                            combinations_in_list[mobile_node_id][random_num]
    return new_strategy_list
