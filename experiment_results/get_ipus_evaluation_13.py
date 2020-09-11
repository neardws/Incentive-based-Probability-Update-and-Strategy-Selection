#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   get_ipus_evaluation.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
9/5/20 4:50 上午   neardws      1.0         None
"""
import json
import numpy as np
import random
import math

from tqdm import tqdm

from algorithm.IPUSS_ver2 import update_useful_channel, random_channel_fading_gain, compute_potential_value
from config.config import settings
from pathlib import Path
import pickle

from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from experiment_results.strategy_evaluation import ipus_get_evaluation

if __name__ == '__main__':

    node_num_list = [15, 15, 15, 17, 16]
    experiment_median = [9, 11, 12, 13, 15]

    only_result_json_files = [settings.RESULT_FILE_VER2_9,
                              settings.RESULT_FILE_VER2_11,
                              settings.RESULT_FILE_VER2_12,
                              settings.RESULT_FILE_VER2_13,
                              settings.RESULT_FILE_VER2_15]

    experiment_median_no = 3
    only_result_json_file = only_result_json_files[3]

    ipus_results = []
    max_complete_ratio = 0
    max_use_efficiency = 0
    max_welfare = 0
    min_welfare = 1000

    json_file = open(only_result_json_file, "r")
    lines = json_file.readlines()
    last_line = lines[-1]
    json_object = json.loads(str(last_line))
    iteration = json_object["iteration"]
    strategy_selection_probability_dict_list = json_object["strategy_selection_probability_dict_list"]
    json_file.close()
    # 得到所有策略可能性
    strategy_no_dict = dict()
    for i, strategy_selection_probability_dict in enumerate(strategy_selection_probability_dict_list):
        if strategy_selection_probability_dict:
            strategy_no_dict[i] = list(strategy_selection_probability_dict.keys())

    pickle_file = Path(load_experiment_median_from_pickle(experiment_median[experiment_median_no]))
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

    """
        {0: ['11408310546', '21172798893', '2856519892', '11470762881'],
         1: ['2155289083562', '5891511300585', '3065817056615', '215763842237'],
         2: ['3105782628', '1235794040', '1040971052'],
         3: ['1614445555157', '1706617533622', '248886037819', '1585914502332', '10509479364'],
         4: ['5674607', '30000955'], 5: ['9563319478', '1353438545', '1071335899'],
         6: ['58999514299', '43582716927', '13472714271'],
         7: ['43889590', '145578403', '103995261', '99828563', '99080372'],
         8: ['50268799837', '137307655349', '132109395926', '57059899441'], 9: ['648975', '4010523'],
         10: ['10882420147941', '5013553374791', '13224076160856', '2250280145320'],
         11: ['49643890767', '29304254181', '22050743051', '49823437623'], 12: ['45241876', '40954716'],
         13: ['7121839054', '58140672312', '26328462730', '57340378983'], 14: ['2245451', '5259460', '10820909'],
         16: ['911320', '711952']}
         """
    strategy_list_list = []
    a15 = math.floor(random.random() * combination_and_strategy_length_of_all_nodes[15]["length_of_strategy_list"])

    for a0 in ['11408310546', '21172798893']:
        for a1 in ['2155289083562', '5891511300585']:
            for a2 in ['3105782628']:
                for a3 in ['1614445555157', '248886037819', '1706617533622']:
                    for a4 in ['5674607']:
                        for a5 in ['9563319478', '1353438545']:
                            for a6 in ['58999514299', '13472714271', '43582716927']:
                                for a7 in ['43889590', '145578403']:
                                    for a8 in ['50268799837', '137307655349']:
                                        for a9 in ['648975']:
                                            for a10 in ['10882420147941', '5013553374791']:
                                                for a11 in ['49643890767', '29304254181']:
                                                    for a12 in ['40954716']:
                                                        for a13 in ['7121839054', '58140672312']:
                                                            for a14 in ['2245451', '5259460']:
                                                                for a16 in ['911320']:
                                                                    strategy_list = []
                                                                    strategy_list.append(int(a0))
                                                                    strategy_list.append(int(a1))
                                                                    strategy_list.append(int(a2))
                                                                    strategy_list.append(int(a3))
                                                                    strategy_list.append(int(a4))
                                                                    strategy_list.append(int(a5))
                                                                    strategy_list.append(int(a6))
                                                                    strategy_list.append(int(a7))
                                                                    strategy_list.append(int(a8))
                                                                    strategy_list.append(int(a9))
                                                                    strategy_list.append(int(a10))
                                                                    strategy_list.append(int(a11))
                                                                    strategy_list.append(int(a12))
                                                                    strategy_list.append(int(a13))
                                                                    strategy_list.append(int(a14))
                                                                    strategy_list.append(int(a15))
                                                                    strategy_list.append(int(a16))
                                                                    strategy_list_list.append(strategy_list)

    for strategy_list in tqdm(strategy_list_list):

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

        for node_numm in range(node_num_list[experiment_median_no]):

            combination_and_strategy_length = combination_and_strategy_length_of_all_nodes[node_numm]

            decimal_num = strategy_list[node_numm]
            x_base = combination_and_strategy_length["length_of_combination"][0]
            x_base_num = list()

            # if decimal_num < 0:
            #     print("decimal_num < 0")

            while True:
                decimal_num, remainder = divmod(decimal_num, x_base)
                x_base_num.append(remainder)
                if decimal_num <= 0:
                    break

            if len(x_base_num) < 10:
                for i in range(10 - len(x_base_num)):
                    x_base_num.append(0)

            x_base_num.reverse()

            # strategy = constructor_of_strategy(x_base_num=x_base_num,
            #                                    combination=combination_and_strategy_length[
            #                                        "combination_of_task_and_time"])
            strategy = []
            for i in x_base_num:
                strategy.append(combination_and_strategy_length[
                                    "combination_of_task_and_time"][i])

            # print("strategy")
            # print(strategy)
            selected_strategy[str(node_numm)] = strategy

        # 更新信道分配

        for i in range(len(selected_strategy)):
            # print(selected_strategy[str(i)])
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
        for mobile_node_id in range(fixed_node_num, node_num_list[experiment_median_no]):

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
        potential_value_list = np.zeros(node_num_list[experiment_median_no])
        for i in range(node_num_list[experiment_median_no]):
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
        for key in selected_strategy.keys():
            strategy = selected_strategy[key]
            for strategy_channel in strategy:
                if strategy_channel[0] != -1:
                    channel_time = strategy_channel[1]
                    channel_utilization_num += channel_time

        channel_utilization_efficiency = sum(task_size) / channel_utilization_num

        social_welfare = sum(potential_value_list)
        # ipus_result = ipus_get_evaluation(strategy_list, experiment_median[experiment_median_no], node_num_list[experiment_median_no])
        # ipus_result = None
        ipus_results.append({"completed_ratio": completed_ratio,
                             "channel_utilization_efficiency": channel_utilization_efficiency,
                             "social_welfare": social_welfare})

        if completed_ratio > max_complete_ratio:
            max_complete_ratio = completed_ratio
        if channel_utilization_efficiency > max_use_efficiency:
            max_use_efficiency = channel_utilization_efficiency
        if social_welfare > max_welfare:
            max_welfare = social_welfare
        if social_welfare < min_welfare:
            min_welfare = social_welfare

    print({"max_complete_ratio": max_complete_ratio,
           "max_use_efficiency": max_use_efficiency,
           "max_welfare": max_welfare,
           "min_welfare": min_welfare})


    """
    {0: ['788963', '885339'], 1: ['34910552', '42115556', '16398881'], 2: ['5121012', '3397258', '3834799'],
    3: ['6549807', '5761047'], 5: ['2809178912', '909535026', '913348726', '1989531476'], 6: ['382951'],
    8: ['38158'], 10: ['26696105', '16390225', '15628171']}
    """
