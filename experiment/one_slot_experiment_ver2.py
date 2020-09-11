#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   one_slot_experiment.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/30 下午7:23   neardws      1.0         None
"""
import json
import math
import os
import random

import numpy as np
from datetime import datetime
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS_ver2 import compute_potential_value, compute_probability_update_value, \
    compute_updated_probability, constructor_of_strategy, update_useful_channel, \
    random_channel_fading_gain
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
import multiprocessing


def print_to_console(msg, objective=None):
    print("*" * 32)
    print(msg)
    if objective is not None:
        print(objective)
        print(type(objective))


def weighted_choice(strategy_list_length, probabilities_wight_dict, discard_set):
    # 得到随机数
    return_value = 0
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
            compare_number -= (strategy_weight - 1)
            if compare_number <= strategy_no - now_no:
                return_value = math.floor(compare_number) + now_no
                if return_value in discard_set:
                    return weighted_choice(strategy_list_length, probabilities_wight_dict, discard_set)
                else:
                    return return_value
            added_sum += strategy_no - 1 + strategy_weight - now_no
            now_no = strategy_no

        compare_number = random_num - added_sum
        return_value = math.floor(compare_number) + now_no
        if return_value in discard_set:
            return weighted_choice(strategy_list_length, probabilities_wight_dict, discard_set)
        else:
            return return_value
    else:
        weight_sum = strategy_list_length
        random_num = random.random() * weight_sum
        return_value = math.floor(random_num)
        if return_value in discard_set:
            return weighted_choice(strategy_list_length, probabilities_wight_dict, discard_set)
        else:
            return return_value


def write_json(json_file_name, dict_data):
    json_file = open(json_file_name, "a")
    json.dump(dict_data, json_file)
    json_file.write("\n")
    # with open(json_file_name, "a") as json_file:
    #     json.dump(dict_data, json_file)
    #     json_file.write("\n")
    #     # json_file.close()


if __name__ == '__main__':

    pickle_file = Path(load_experiment_median_from_pickle(4))
    fp = pickle_file.open("rb")
    iteration = pickle.load(fp)
    fixed_edge_node = pickle.load(fp)
    edge_vehicle_node = pickle.load(fp)
    fixed_distance_matrix = pickle.load(fp)
    mobile_distance_matrix = pickle.load(fp)
    task_list = pickle.load(fp)
    node_num = pickle.load(fp)
    fixed_node_num = pickle.load(fp)
    mobile_node_num = pickle.load(fp)
    max_potential_value = pickle.load(fp)
    useful_channel_under_node = pickle.load(fp)
    task_id_under_each_node_list = pickle.load(fp)
    usable_channel_of_all_nodes = pickle.load(fp)
    task_time_limitation_of_all_nodes = pickle.load(fp)
    combination_and_strategy_length_of_all_nodes = pickle.load(fp)
    """
      ————————————————————————————————————————————————————————————————————————————————————
          单时间片实验开始
      ————————————————————————————————————————————————————————————————————————————————————
    """
    union_task_id_set = set()
    for task_id_under_each_node in task_id_under_each_node_list:
        task_id_set = set(task_id_under_each_node)
        union_task_id_set = union_task_id_set | task_id_set

    if not os.path.exists(settings.JSON_FILE_VER2):
        json_file = open(settings.JSON_FILE_VER2, "a+")
        json_file.close()
        iteration = 0
        print_to_console(" 初始化最大策略值")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for i in range(node_num):
            max_potential_value[i] = 1

        strategy_selection_probability_dict_list = list()
        for i in range(node_num):
            strategy_selection_probability_dict = dict()
            strategy_selection_probability_dict_list.append(strategy_selection_probability_dict)

        discard_set_list = list()
        for i in range(node_num):
            discard_set = set()
            discard_set_list.append(discard_set)

    else:

        json_file = open(settings.JSON_FILE_VER2, "r+")
        lines = json_file.readlines()
        #json_file.writelines([item for item in lines[:-1]])
        last_line = lines[-1].rstrip("\n")
        json_object = json.loads(str(last_line))
        iteration = json_object["iteration"]
        max_potential_value = np.array(json_object["max_potential_value"])
        strategy_selection_probability_dict_list = json_object["strategy_selection_probability_dict_list"]
        old_discard_set_list = json_object["discard_set_list"]

        json_file.close()

        discard_set_list = []
        for discard_set in old_discard_set_list:
            discard_set_list.append(set(discard_set))

    # 开始单次时间片实验
    node_num = node_num - 1
    json_file_name = settings.JSON_FILE_VER2
    
    pool = multiprocessing.Pool(5)

    experiment_iteration_max = 10e5
    learning_rate = settings.LEARNING_RATE

    white_gaussian_noise = settings.WHITE_GAUSSIAN_NOISE
    antenna_constant = settings.ANTENNA_CONSTANT
    path_loss_exponent = settings.PATH_LOSS_EXPONENT
    sub_channel_bandwidth = settings.SUB_CHANNEL_BANDWIDTH

    print_to_console("第" + str(iteration) + "迭代开始")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    while iteration < experiment_iteration_max:
        """
          ————————————————————————————————————————————————————————————————————————————————————
              单次迭代
          ————————————————————————————————————————————————————————————————————————————————————
        """
        selected_strategy = dict()
        selected_strategy_no = dict()

        """
        ————————————————————————————————————————————————————————————————————————————————————
             选择策略
        ———————————————————————————————————————————————————————————————————————————————————— 
        """

        for i in range(node_num):
            # xxxx = i
            combination_and_strategy_length = combination_and_strategy_length_of_all_nodes[i]

            strategy_selection_probability = strategy_selection_probability_dict_list[i]
            # xxxx1 = combination_and_strategy_length["length_of_strategy_list"][0]
            # xxxx2 = strategy_selection_probability_dict_list[i]
            # xxxx3 = discard_set_list[i]
            strategy_no = weighted_choice(combination_and_strategy_length["length_of_strategy_list"][0],
                                          strategy_selection_probability_dict_list[i],
                                          discard_set_list[i])

            decimal_num = strategy_no
            x_base = combination_and_strategy_length["length_of_combination"][0]
            x_base_num = list()

            if decimal_num < 0:
                print_to_console("decimal_num < 0")

            while True:
                decimal_num, remainder = divmod(decimal_num, x_base)
                x_base_num.append(remainder)
                if decimal_num <= 0:
                    break

            x_base_num.reverse()

            # x_base_num = decimal2xBase(decimal_num=strategy_no,
            #                            x_base=combination_and_strategy_length[
            #                                "length_of_combination"][0])
            strategy = constructor_of_strategy(x_base_num=x_base_num,
                                               combination=combination_and_strategy_length[
                                                   "combination_of_task_and_time"])
            selected_strategy[str(i)] = strategy
            selected_strategy_no[str(i)] = strategy_no

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
                # print_to_console("task_transmission_data", task_transmission_data)
                task_id = task_transmission_data["task_id"]
                task_data_size = task_transmission_data["task_data_size"]
                task_size[task_id] += task_data_size

        for i, size in enumerate(task_size):
            task_need_size = task_list[i]["data_size"]
            task_need_size_list[i] = task_need_size * 1024 * 1024 * 0.5
            diff_size.append(task_need_size * 1024 * 1024 * 0.5 - size)
            if size >= task_need_size * 1024 * 1024 * 0.5:
                finished[i] = 1

        # finished_in_each_node = np.zeros(node_num)
        # for node_no, task_id_under_each_node in enumerate(task_id_under_each_node_list):
        #     for task_id in task_id_under_each_node:
        #         if finished[task_id] == 1:
        #             finished_in_each_node[node_no] += 1
        """:cvar
        *****************************************************************************************************************************************
        """

        # 计算激励值并更新策略选择概率
        # print_to_console("迭代" + str(iteration) + " 计算激励值并更新策略选择概率")
        # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        potential_value_list = np.zeros(node_num)
        for i in range(node_num):
            strategy_selection_probability = strategy_selection_probability_dict_list[i]
            potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
            potential_value_list[i] = potential_value
            probability_update_value = compute_probability_update_value(potential_value=potential_value,
                                                                        max_potential_value=max_potential_value[
                                                                            i])
            strategy_no = selected_strategy_no[str(i)]
            if str(strategy_no) in strategy_selection_probability.keys():
                origin_probability = strategy_selection_probability[str(strategy_no)]
            else:
                origin_probability = 1
            new_probability = compute_updated_probability(origin_probability, learning_rate,
                                                          probability_update_value)
            if new_probability > 1:
                strategy_selection_probability[str(strategy_no)] = new_probability
            elif new_probability < 1:
                if str(strategy_no) in strategy_selection_probability.keys():
                    del strategy_selection_probability_dict_list[i][str(strategy_no)]
                discard_set_list[i].add(strategy_no)
            else:
                pass

            max_potential_value[i] = max(potential_value, max_potential_value[i])

        iteration += 1

        """
                iteration
                max_potential_value
                strategy_selection_probability_dict_list
                """

        if iteration < 1000:
            if iteration % 10 == 0:
                print_to_console("迭代" + str(iteration) + " 结束")
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if iteration % 100 == 0:
                print_to_console("迭代" + str(iteration) + " 结束")
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                new_discard_set_list = []
                for discard_set in discard_set_list:
                    new_discard_set_list.append(list(discard_set))

                selected_strategy_no_list = []
                for node_no in range(node_num):
                    selected_strategy_no_list.append(selected_strategy_no[str(node_no)])

                finished_num = 0
                for isFinished in finished:
                    if isFinished:
                        finished_num += 1

                json_dict = {"iteration": int(iteration),
                             "finished_num": finished_num,
                             "sum_max_potential_value": sum(max_potential_value),
                             "strategy_selection_probability_dict_list": list(
                                 strategy_selection_probability_dict_list),
                             "strategy": selected_strategy_no,
                             "finished": list(finished),
                             "potential_value_list":list(potential_value_list),
                             "max_potential_value": list(max_potential_value),
                             "discard_set_list": new_discard_set_list}
                # print_to_console(json_dict)
                # print_to_console(type(json_dict))

                pool.apply_async(write_json, args=(json_file_name, json_dict))
                # json_process = multiprocessing.Process(target=write_json, args=(json_file_name, json_dict))
                # json_process.start()
                # json_process.join()
                print_to_console( str(iteration) + " 写入JSON进程结束")

        else:
            if iteration % 10 == 0:
                print_to_console("迭代" + str(iteration) + " 结束")
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if iteration % 100 == 0:
                print_to_console("迭代" + str(iteration) + " 结束")
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                new_discard_set_list = []
                for discard_set in discard_set_list:
                    new_discard_set_list.append(list(discard_set))

                selected_strategy_no_list = []
                for node_no in range(node_num):
                    selected_strategy_no_list.append(selected_strategy_no[str(node_no)])

                finished_num = 0
                for isFinished in finished:
                    if isFinished:
                        finished_num += 1

                json_dict = {"iteration": int(iteration),
                             "finished_num": finished_num,
                             "sum_max_potential_value": sum(max_potential_value),
                             "strategy_selection_probability_dict_list": list(
                                 strategy_selection_probability_dict_list),
                             "strategy": selected_strategy_no,
                             "finished": list(finished),
                             "potential_value_list": list(potential_value_list),
                             "max_potential_value": list(max_potential_value),
                             "discard_set_list": new_discard_set_list}
                # print_to_console(json_dict)
                # print_to_console(type(json_dict))
                pool.apply_async(write_json, args=(json_file_name, json_dict))
                print_to_console(str(iteration) + " 写入JSON进程结束")

    pool.close()
    pool.join()