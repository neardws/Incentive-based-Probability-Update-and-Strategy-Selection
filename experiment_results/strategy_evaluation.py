#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   strategy_evaluation.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/4/20 4:23 下午   neardws      1.0         None
"""

import numpy as np
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS_ver2 import compute_potential_value, constructor_of_strategy, update_useful_channel, \
    random_channel_fading_gain
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle


def common_get_evaluation(strategy_list, experiment_median_num, node_num):
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
    sub_channel_bandwidth = settings.SUB_CHANNEL_BANDWIDTH

    selected_strategy = dict()
    """
    ————————————————————————————————————————————————————————————————————————————————————
         选择策略
    ———————————————————————————————————————————————————————————————————————————————————— 
    """

    for i, strategy in enumerate(strategy_list):

        selected_strategy[str(i)] = strategy

    # 更新信道分配
    for i in range(len(selected_strategy)):
        useful_channel_under_node[i] = update_useful_channel(selected_strategy[str(i)],
                                                             useful_channel_under_node[i])

    task_transmission_data_dict_of_all_nodes = dict()

    """
    ________________________________________________________________________________________________________________________________________-
                计算传输数据
    *****************************************************************************************************************************************
    """
    node_type = settings.NODE_TYPE_FIXED
    for fixed_node_id in range(fixed_node_num):

        # print_to_console(task_id_under_each_node_list)
        task_id_list = task_id_under_each_node_list[fixed_node_id]
        node_strategy = selected_strategy[str(fixed_node_id)]

        task_transmission_data_list = []

        for task_id in task_id_list:

            task_data_size = 0

            for node_strategy_no in range(len(node_strategy)):  # 对于节点的每个信道上的分配
                allocated_channel_no = useful_channel_under_node[fixed_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号
                if task_id == node_strategy[node_strategy_no][0]:  # 为这个任务分配了信道
                    task_time = node_strategy[node_strategy_no][1]  # 信道的分配时长

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
                    channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                    task_data_size += channel_data_size
            task_transmission_data = {"task_id": task_id,
                                      "task_data_size": task_data_size}
            task_transmission_data_list.append(task_transmission_data)

        task_transmission_data_dict_of_all_nodes[str(fixed_node_id)] = task_transmission_data_list

    node_type = settings.NODE_TYPE_MOBILE
    for mobile_node_id in range(fixed_node_num, node_num):

        task_id_list = task_id_under_each_node_list[mobile_node_id]
        node_strategy = selected_strategy[str(mobile_node_id)]

        task_transmission_data_list = []

        for task_id in task_id_list:

            task_data_size = 0

            for node_strategy_no in range(len(node_strategy)):

                allocated_channel_no = useful_channel_under_node[mobile_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号

                if task_id == node_strategy[node_strategy_no][0]:

                    task_time = node_strategy[node_strategy_no][1]

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
                    # print(SINR)
                    channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                    task_data_size += channel_data_size

            task_transmission_data = {"task_id": task_id,
                                      "task_data_size": task_data_size}
            task_transmission_data_list.append(task_transmission_data)

        task_transmission_data_dict_of_all_nodes[str(mobile_node_id)] = task_transmission_data_list

    """
    *****************************************************************************************************************************************
    计算 任务完成数
    *****************************************************************************************************************************************

    """

    finished = np.zeros(len(task_list))

    task_size = np.zeros(len(task_list))
    task_need_size_list = np.zeros(len(task_list))
    diff_size = []
    for key in task_transmission_data_dict_of_all_nodes.keys():
        task_transmission_data_list = task_transmission_data_dict_of_all_nodes[key]

        for task_transmission_data in task_transmission_data_list:
            task_id = task_transmission_data["task_id"]
            task_data_size = task_transmission_data["task_data_size"]
            task_size[task_id] += task_data_size

    for i, size in enumerate(task_size):
        task_need_size = task_list[i]["data_size"]
        task_need_size_list[i] = task_need_size * 1024 * 1024 * 0.5
        diff_size.append(task_need_size * 1024 * 1024 * 0.5 - size)
        if size >= task_need_size * 1024 * 1024 * 0.5:
            finished[i] = 1

    """
    *****************************************************************************************************************************************
    """
    potential_value_list = np.zeros(node_num)
    for i in range(node_num):
        potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
        potential_value_list[i] = potential_value
        max_potential_value[i] = max(potential_value, max_potential_value[i])

    """
    *****************************************************************************************************************************************
    completed_ratio: 任务完成率 = 所有完成任务 / 车辆范围内所有任务
    channel_utilization_efficiency: 信道利用率 = 传输数据量 / （信道数量 * 时间）
    social_welfare: 社会福利 = 所有节点的势函数值之和
    """
    completed_num = 0
    for isFinish in finished:
        if isFinish == 1:
            completed_num += 1
    completed_ratio = completed_num / len(union_task_id_set)

    channel_utilization_num = 0
    for strategy in strategy_list:
        for strategy_channel in strategy:
            if strategy_channel[0] != -1:
                channel_time = strategy_channel[1]
                channel_utilization_num += channel_time

    channel_utilization_efficiency = sum(task_size) / channel_utilization_num

    social_welfare = sum(potential_value_list)

    return {"completed_ratio": completed_ratio,
            "channel_utilization_efficiency": channel_utilization_efficiency,
            "social_welfare": social_welfare}


def ipus_get_evaluation(strategy_list, experiment_median_num, node_num):
    """
    :argument
        strategy_list: 每个节点选择策略组成的列表
        experiment_median_num： 从第几个experiment_median文件中读取实验设置
        node_num：对应experiment_median 实验中具有任务的节点数量
    :return
        completed_ratio: 任务完成率 = 所有完成任务 / 车辆范围内所有任务
        channel_utilization_efficiency: 信道利用率 = 传输数据量 / （信道数量 * 时间）
        social_welfare: 社会福利 = 所有节点的势函数值之和
    """
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
    sub_channel_bandwidth = settings.SUB_CHANNEL_BANDWIDTH

    selected_strategy = dict()
    selected_strategy_no = dict()
    """
    ————————————————————————————————————————————————————————————————————————————————————
         选择策略
    ———————————————————————————————————————————————————————————————————————————————————— 
    """

    for i in range(node_num):

        combination_and_strategy_length = combination_and_strategy_length_of_all_nodes[i]

        decimal_num = strategy_list[i]
        x_base = combination_and_strategy_length["length_of_combination"][0]
        x_base_num = list()

        if decimal_num < 0:
            print("decimal_num < 0")

        while True:
            decimal_num, remainder = divmod(decimal_num, x_base)
            x_base_num.append(remainder)
            if decimal_num <= 0:
                break

        if len(x_base_num) < 10:
            for i in range(10 - len(x_base_num)):
                x_base_num.append(0)

        x_base_num.reverse()

        strategy = constructor_of_strategy(x_base_num=x_base_num,
                                           combination=combination_and_strategy_length[
                                                   "combination_of_task_and_time"])
        print("strategy")
        print(strategy)
        selected_strategy[str(i)] = strategy
        selected_strategy_no[str(i)] = strategy_list[i]

    # 更新信道分配
    print(selected_strategy)
    for i in range(len(selected_strategy)):
        print(selected_strategy[str(i)])
        useful_channel_under_node[i] = update_useful_channel(selected_strategy[str(i)],
                                                             useful_channel_under_node[i])

    task_transmission_data_dict_of_all_nodes = dict()

    """
    ________________________________________________________________________________________________________________________________________-
                计算传输数据
    *****************************************************************************************************************************************
    """
    node_type = settings.NODE_TYPE_FIXED
    for fixed_node_id in range(fixed_node_num):

        # print_to_console(task_id_under_each_node_list)
        task_id_list = task_id_under_each_node_list[fixed_node_id]
        node_strategy = selected_strategy[str(fixed_node_id)]

        task_transmission_data_list = []

        for task_id in task_id_list:

            task_data_size = 0

            for node_strategy_no in range(len(node_strategy)):  # 对于节点的每个信道上的分配
                allocated_channel_no = useful_channel_under_node[fixed_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号
                if task_id == node_strategy[node_strategy_no][0]:  # 为这个任务分配了信道
                    task_time = node_strategy[node_strategy_no][1]  # 信道的分配时长

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
                    channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                    task_data_size += channel_data_size
            task_transmission_data = {"task_id": task_id,
                                      "task_data_size": task_data_size}
            task_transmission_data_list.append(task_transmission_data)

        task_transmission_data_dict_of_all_nodes[str(fixed_node_id)] = task_transmission_data_list

    node_type = settings.NODE_TYPE_MOBILE
    for mobile_node_id in range(fixed_node_num, node_num):

        task_id_list = task_id_under_each_node_list[mobile_node_id]
        node_strategy = selected_strategy[str(mobile_node_id)]

        task_transmission_data_list = []

        for task_id in task_id_list:

            task_data_size = 0

            for node_strategy_no in range(len(node_strategy)):

                allocated_channel_no = useful_channel_under_node[mobile_node_id]["node_channel"][
                    node_strategy_no]  # 该行策略分配对应的信道编号

                if task_id == node_strategy[node_strategy_no][0]:

                    task_time = node_strategy[node_strategy_no][1]

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
                    # print(SINR)
                    channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                    task_data_size += channel_data_size

            task_transmission_data = {"task_id": task_id,
                                      "task_data_size": task_data_size}
            task_transmission_data_list.append(task_transmission_data)

        task_transmission_data_dict_of_all_nodes[str(mobile_node_id)] = task_transmission_data_list

    """
    *****************************************************************************************************************************************
    计算 任务完成数
    *****************************************************************************************************************************************

    """

    finished = np.zeros(len(task_list))

    task_size = np.zeros(len(task_list))
    task_need_size_list = np.zeros(len(task_list))
    diff_size = []
    for key in task_transmission_data_dict_of_all_nodes.keys():
        task_transmission_data_list = task_transmission_data_dict_of_all_nodes[key]

        for task_transmission_data in task_transmission_data_list:
            task_id = task_transmission_data["task_id"]
            task_data_size = task_transmission_data["task_data_size"]
            task_size[task_id] += task_data_size

    for i, size in enumerate(task_size):
        task_need_size = task_list[i]["data_size"]
        task_need_size_list[i] = task_need_size * 1024 * 1024 * 0.5
        diff_size.append(task_need_size * 1024 * 1024 * 0.5 - size)
        if size >= task_need_size * 1024 * 1024 * 0.5:
            finished[i] = 1

    """
    *****************************************************************************************************************************************
    """
    potential_value_list = np.zeros(node_num)
    for i in range(node_num):
        potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
        potential_value_list[i] = potential_value
        max_potential_value[i] = max(potential_value, max_potential_value[i])

    """
    *****************************************************************************************************************************************
    completed_ratio: 任务完成率 = 所有完成任务 / 车辆范围内所有任务
    channel_utilization_efficiency: 信道利用率 = 传输数据量 / （信道数量 * 时间）
    social_welfare: 社会福利 = 所有节点的势函数值之和
    """
    completed_num = 0
    print("finished")
    print(finished)
    for isFinish in finished:
        if isFinish == 1:
            completed_num += 1
    completed_ratio = completed_num / len(union_task_id_set)

    channel_utilization_num = 0
    for strategy in strategy_list:
        for strategy_channel in strategy:
            if strategy_channel[0] != -1:
                channel_time = strategy_channel[1]
                channel_utilization_num += channel_time

    channel_utilization_efficiency = sum(task_size) / channel_utilization_num

    social_welfare = sum(potential_value_list)

    return {"completed_ratio": completed_ratio,
            "channel_utilization_efficiency": channel_utilization_efficiency,
            "social_welfare": social_welfare}