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
from datetime import datetime

import numpy as np
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS import weighted_choice, compute_task_is_finished, \
    compute_task_transmission_data, compute_potential_value, compute_probability_update_value, \
    compute_updated_probability
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from tqdm import tqdm


def print_to_console(msg, objective=None):
    print("*" * 32)
    print(msg)
    print(objective)
    print(type(objective))


if __name__ == '__main__':

    pickle_file = Path(load_experiment_median_from_pickle(1))
    fp = pickle_file.open("rb")
    iteration = pickle.load(fp)
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
    strategy_space_of_all_nodes = pickle.load(fp)
    strategy_selection_probability_of_all_node = pickle.load(fp)
    """
      ————————————————————————————————————————————————————————————————————————————————————
          单时间片实验开始
      ————————————————————————————————————————————————————————————————————————————————————
    """

    # 开始单次时间片实验
    experiment_iteration_max = 10e5
    learning_rate = settings.LEARNING_RATE
    pbar = tqdm(total=100)

    while iteration < experiment_iteration_max:
        """
          ————————————————————————————————————————————————————————————————————————————————————
              单次迭代
          ————————————————————————————————————————————————————————————————————————————————————
        """
        if iteration == 0:
            # 随机选择策略
            selected_strategy = []
            selected_strategy_no = []
            for i in range(node_num):
                strategy_no = weighted_choice(strategy_selection_probability_of_all_node[i])
                strategy = strategy_space_of_all_nodes[i][strategy_no]
                selected_strategy.append(strategy)
                selected_strategy_no.append(strategy_no)

            # 计算激励值
            task_transmission_data_list_of_all_nodes = []
            for i in range(fixed_node_num):
                task_transmission_data = compute_task_transmission_data(task_id_list=task_id_under_each_node_list[i],
                                                                        strategy=selected_strategy[i],
                                                                        node_type=settings.NODE_TYPE_FIXED,
                                                                        node_no=i,
                                                                        fixed_node=fixed_edge_node,
                                                                        mobile_node=edge_vehicle_node,
                                                                        useful_channel_list_under_fixed_node=useful_channel_under_node[
                                                                                                             :fixed_node_num],
                                                                        useful_channel_list_under_mobile_node=useful_channel_under_node[
                                                                                                              fixed_node_num:],
                                                                        fixed_distance_matrix=fixed_distance_matrix,
                                                                        mobile_distance_matrix=mobile_distance_matrix)
                task_transmission_data_list_of_all_nodes.append(task_transmission_data)
            for i in range(mobile_node_num):
                task_transmission_data = compute_task_transmission_data(
                    task_id_list=task_id_under_each_node_list[fixed_node_num + i],
                    strategy=selected_strategy[fixed_node_num + i],
                    node_type=settings.NODE_TYPE_MOBILE,
                    node_no=i,
                    fixed_node=fixed_edge_node,
                    mobile_node=edge_vehicle_node,
                    useful_channel_list_under_fixed_node=useful_channel_under_node[
                                                         :fixed_node_num],
                    useful_channel_list_under_mobile_node=useful_channel_under_node[
                                                          fixed_node_num:],
                    fixed_distance_matrix=fixed_distance_matrix,
                    mobile_distance_matrix=mobile_distance_matrix)
                task_transmission_data_list_of_all_nodes.append(task_transmission_data)
            finished = compute_task_is_finished(task_list=task_list,
                                                task_transmission_data_list_of_all_nodes=task_transmission_data_list_of_all_nodes)

            for i in range(node_num):
                potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)

                # 初始化最大的策略值
                max_potential_value[i] = potential_value

        else:
            # 随机选择策略
            selected_strategy = []
            selected_strategy_no = []
            for i in range(node_num):
                strategy_no = weighted_choice(strategy_selection_probability_of_all_node[i])
                strategy = strategy_space_of_all_nodes[i][strategy_no]
                selected_strategy.append(strategy)
                selected_strategy_no.append(strategy_no)

            # 计算激励值
            task_transmission_data_list_of_all_nodes = []
            for i in range(fixed_node_num):
                task_transmission_data = compute_task_transmission_data(task_id_list=task_id_under_each_node_list[i],
                                                                        strategy=selected_strategy[i],
                                                                        node_type=settings.NODE_TYPE_FIXED,
                                                                        node_no=i,
                                                                        fixed_node=fixed_edge_node,
                                                                        mobile_node=edge_vehicle_node,
                                                                        useful_channel_list_under_fixed_node=useful_channel_under_node[
                                                                                                             :fixed_node_num],
                                                                        useful_channel_list_under_mobile_node=useful_channel_under_node[
                                                                                                              fixed_node_num:],
                                                                        fixed_distance_matrix=fixed_distance_matrix,
                                                                        mobile_distance_matrix=mobile_distance_matrix)
                task_transmission_data_list_of_all_nodes.append(task_transmission_data)
            for i in range(mobile_node_num):
                task_transmission_data = compute_task_transmission_data(
                    task_id_list=task_id_under_each_node_list[fixed_node_num + i],
                    strategy=selected_strategy[fixed_node_num + i],
                    node_type=settings.NODE_TYPE_MOBILE,
                    node_no=i,
                    fixed_node=fixed_edge_node,
                    mobile_node=edge_vehicle_node,
                    useful_channel_list_under_fixed_node=useful_channel_under_node[
                                                         :fixed_node_num],
                    useful_channel_list_under_mobile_node=useful_channel_under_node[
                                                          fixed_node_num:],
                    fixed_distance_matrix=fixed_distance_matrix,
                    mobile_distance_matrix=mobile_distance_matrix)
                task_transmission_data_list_of_all_nodes.append(task_transmission_data)
            finished = compute_task_is_finished(task_list=task_list,
                                                task_transmission_data_list_of_all_nodes=task_transmission_data_list_of_all_nodes)
            # 计算激励值并更新策略选择概率
            for i in range(node_num):
                potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
                probability_update_value = compute_probability_update_value(potential_value=potential_value,
                                                                            max_potential_value=max_potential_value[i])
                strategy_list = strategy_space_of_all_nodes[i]
                origin_probability = strategy_list[selected_strategy_no[i]]
                new_probability = compute_updated_probability(origin_probability, learning_rate, probability_update_value)
                strategy_space_of_all_nodes[i][selected_strategy_no[i]] = new_probability

        pbar.update(0.001)
        iteration += 1
