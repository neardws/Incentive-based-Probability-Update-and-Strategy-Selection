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
import numpy as np
from datetime import datetime
from pympler import tracker
import multiprocessing
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS import weighted_choice, compute_task_is_finished, \
    compute_task_transmission_data, compute_potential_value, compute_probability_update_value, \
    compute_updated_probability, constructor_of_strategy, decimal2xBase, update_useful_channel
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from tqdm import tqdm


def print_to_console(msg, objective=None):
    print("*" * 32)
    print(msg)
    if objective is not None:
        print(objective)
        print(type(objective))
        

def process_compute_task_transmission_data(i,
                                           task_id_under_each_node,
                                           selected_strategy,
                                           node_type,
                                           fixed_edge_node,
                                           edge_vehicle_node,
                                           useful_channel_under_node,
                                           fixed_node_num,
                                           fixed_distance_matrix,
                                           mobile_distance_matrix):
    task_transmission_data = compute_task_transmission_data(task_id_list=task_id_under_each_node,
                                                            strategy=selected_strategy,
                                                            node_type=node_type,
                                                            node_no=i,
                                                            fixed_node=fixed_edge_node,
                                                            mobile_node=edge_vehicle_node,
                                                            useful_channel_list_under_fixed_node=
                                                            useful_channel_under_node[:fixed_node_num],
                                                            useful_channel_list_under_mobile_node=
                                                            useful_channel_under_node[fixed_node_num:],
                                                            fixed_distance_matrix=fixed_distance_matrix,
                                                            mobile_distance_matrix=mobile_distance_matrix)
    return {"i": i,
            "task_transmission_data": task_transmission_data}


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
    # tr = tracker.SummaryTracker()
    # tr.print_diff()

    # 开始单次时间片实验
    node_num = node_num - 1

    processes_number = 3
    # experiment_iteration_max = 10e5
    experiment_iteration_max = 100
    learning_rate = settings.LEARNING_RATE

    # pbar = tqdm(total=100)

    while iteration < experiment_iteration_max:
        """
          ————————————————————————————————————————————————————————————————————————————————————
              单次迭代
          ————————————————————————————————————————————————————————————————————————————————————
        """
        print_to_console("第" + str(iteration) + "迭代开始")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # 初始化策略列表与策略选择概率
        print_to_console("迭代" + str(iteration) + " 初始化策略列表与策略选择概率")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        selected_strategy = dict()
        selected_strategy_no = dict()

        strategy_selection_probability_dict_list = list()
        for i in range(node_num):
            strategy_selection_probability_dict = dict()
            strategy_selection_probability_dict_list.append(strategy_selection_probability_dict)
        """
        ————————————————————————————————————————————————————————————————————————————————————
             选择策略
        ———————————————————————————————————————————————————————————————————————————————————— 
        """

        for i in range(node_num):
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(str(i) + "选择策略开始")
            combination_and_strategy_length = combination_and_strategy_length_of_all_nodes[i]
            strategy_no = weighted_choice(combination_and_strategy_length["length_of_strategy_list"][0],
                                          strategy_selection_probability_dict_list[i])
            x_base_num = decimal2xBase(decimal_num=strategy_no,
                          x_base=combination_and_strategy_length[
                              "length_of_combination"][0])
            strategy = constructor_of_strategy(x_base_num=x_base_num,
                                               combination=combination_and_strategy_length["combination_of_task_and_time"])
            selected_strategy[str(i)] = strategy
            selected_strategy_no[str(i)] = strategy_no

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("选择策略完成")

        # 更新信道分配
        for i in range(len(selected_strategy)):
            update_useful_channel(selected_strategy[str(i)], useful_channel_under_node[i])

        # 计算激励值
        print_to_console("迭代" + str(iteration) + " 计算激励值")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        task_transmission_data_dict_of_all_nodes = dict()

        """
        ——————————————————————————————————————————————————————————————————————————————————
            多进程运行 计算传输数据量 
        ——————————————————————————————————————————————————————————————————————————————————
        """

        pool_compute_task_data = multiprocessing.Pool(processes=processes_number)
        jobs_compute_task_data = []

        node_type = settings.NODE_TYPE_FIXED
        for i in range(fixed_node_num):
            """:cvar
            ________________________________________________________________________________________________________________________________________-
            """
            # task_transmission_data = compute_task_transmission_data(task_id_list=task_id_under_each_node_list[i],
            #                                                         strategy=selected_strategy[str(i)],
            #                                                         node_type=node_type,
            #                                                         node_no=i,
            #                                                         fixed_node=fixed_edge_node,
            #                                                         mobile_node=edge_vehicle_node,
            #                                                         useful_channel_list_under_fixed_node=
            #                                                         useful_channel_under_node[:fixed_node_num],
            #                                                         useful_channel_list_under_mobile_node=
            #                                                         useful_channel_under_node[fixed_node_num:],
            #                                                         fixed_distance_matrix=fixed_distance_matrix,
            #                                                         mobile_distance_matrix=mobile_distance_matrix)
            """:cvar
            *****************************************************************************************************************************************
            """
            sub_channel_bandwidth = settings.SUB_CHANNEL_BANDWIDTH

            task_transmission_data_list = []
            for task_id in task_id_under_each_node_list[i]:
                task_data_size = 0
                x = len(selected_strategy[str(i)])
                print(selected_strategy[str(i)])
                print(type(selected_strategy[str(i)]))
                for channel_no in range(x):
                    if task_id == selected_strategy[str(i)][channel_no][0]:
                        task_time = selected_strategy[str(i)][channel_no][1]
                        SINR = 0

                        white_gaussian_noise = settings.WHITE_GAUSSIAN_NOISE

                        signal = 0
                        interference = 0

                        signal_list = []

                        antenna_constant = settings.ANTENNA_CONSTANT
                        path_loss_exponent = settings.PATH_LOSS_EXPONENT

                        for node_no, useful_channel in enumerate(useful_channel_under_node[:fixed_node_num]):
                            node_channel = useful_channel["node_channel"]
                            channel_status = useful_channel["channel_status"]
                            for i, channel_no in enumerate(node_channel):
                                if channel_no == channel_no:
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
                                if channel_no == channel_no:
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



                        for signal_dict in signal_list:
                            if signal_dict["node_type"] == node_type:
                                if signal_dict["node_id"] == i:
                                    signal = signal_dict["signal"]
                                else:
                                    interference += signal_dict["signal"]
                            else:
                                interference += signal_dict["signal"]

                        SINR = signal / (interference + white_gaussian_noise)
                        print(SINR)
                        channel_data_size = task_time * sub_channel_bandwidth * np.log2(1 + SINR)
                        task_data_size += channel_data_size
                task_transmission_data = {"task_id": task_id,
                                          "task_data_size": task_data_size}
                task_transmission_data_list.append(task_transmission_data)



            """:cvar
                       *****************************************************************************************************************************************
                       """
            task_transmission_data_dict_of_all_nodes[str(i)] = task_transmission_data

        node_type = settings.NODE_TYPE_MOBILE
        for i in range(fixed_node_num, node_num):
            task_transmission_data = compute_task_transmission_data(task_id_list=task_id_under_each_node_list[i],
                                                                    strategy=selected_strategy[str(i)],
                                                                    node_type=node_type,
                                                                    node_no=i,
                                                                    fixed_node=fixed_edge_node,
                                                                    mobile_node=edge_vehicle_node,
                                                                    useful_channel_list_under_fixed_node=
                                                                    useful_channel_under_node[:fixed_node_num],
                                                                    useful_channel_list_under_mobile_node=
                                                                    useful_channel_under_node[fixed_node_num:],
                                                                    fixed_distance_matrix=fixed_distance_matrix,
                                                                    mobile_distance_matrix=mobile_distance_matrix)
            task_transmission_data_dict_of_all_nodes[str(i)] = task_transmission_data

        finished = compute_task_is_finished(task_list=task_list,
                                            task_transmission_data_dict_of_all_nodes=
                                            task_transmission_data_dict_of_all_nodes)

        if iteration == 0:
            print_to_console("迭代" + str(iteration) + " 初始化最大策略值")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for i in range(node_num):
                if len(task_id_under_each_node_list[i]) != 0:
                    potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
                    # 初始化最大的策略值
                    max_potential_value[i] = potential_value
        else:
            # 计算激励值并更新策略选择概率
            print_to_console("迭代" + str(iteration) + " 计算激励值并更新策略选择概率")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for i in range(node_num):
                if str(i) in selected_strategy_no.keys():
                    strategy_selection_probability = strategy_selection_probability_dict_list[i]
                    potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
                    probability_update_value = compute_probability_update_value(potential_value=potential_value,
                                                                                max_potential_value=max_potential_value[
                                                                                    i])
                    strategy_no = selected_strategy_no[str(i)]
                    if strategy_no in strategy_selection_probability.keys():
                        origin_probability = strategy_selection_probability[str(strategy_no)]["weight"]
                    else:
                        origin_probability = 1
                    new_probability = compute_updated_probability(origin_probability, learning_rate,
                                                                  probability_update_value)
                    strategy_selection_probability_dict_list[i][str(strategy_no)] = new_probability

                    # 排序
                    keys = strategy_selection_probability_dict_list[i].keys()
                    keys.sort()
                    strategy_selection_probability_dict_list[i] = map(strategy_selection_probability_dict_list[i].get(),
                                                                      keys)

                    max_potential_value[i] = max(potential_value, max_potential_value[i])

        print_to_console("迭代" + str(iteration) + " 结束")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # pbar.update(0.001)
        iteration += 1
