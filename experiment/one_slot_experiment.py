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
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS import init_useful_channel, get_usable_channel_list, generator_of_strategy_list, \
    generator_of_strategy_selection_probability, weighted_choice, compute_task_is_finished, \
    compute_task_transmission_data, compute_potential_value, compute_probability_update_value, \
    compute_updated_probability
from init_input.experiment_input_save_and_reload import load_pickle
from init_input.init_distance import get_task_id_under_edge_node, get_task_time_limitation_under_edge_node
from tqdm import tqdm


def print_to_console(msg, object):
    print("*" * 32)
    print(msg)
    print(object)
    print(type(object))


def print_to_console(msg):
    print("*" * 32)
    print(msg)


if __name__ == '__main__':

    # 读取实验参数设置
    # fixed_edge_node = None
    # edge_vehicle_node = None
    # task_by_time_list = None
    # fixed_distance_matrix_list = None
    # mobile_distance_matrix_list = None

    pickle_file = Path(load_pickle(5))
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

    fp.close()

    """
        ————————————————————————————————————————————————————————————————————————————————————
            实验进行初始化
            1、初始化迭代次数
            2、初始化边缘节点数量
            3、初始化激励值集合
            4、初始化可用信道
            5、初始化每个节点下的任务
            6、初始化节点当前可用信道列表
            7、初始化策略空间
            8、初始化选择概率
        ————————————————————————————————————————————————————————————————————————————————————
    """
    # 初始化迭代次数
    iteration = 0
    fixed_distance_matrix = fixed_distance_matrix_list[iteration]
    mobile_distance_matrix = mobile_distance_matrix_list[iteration]
    task_list = task_by_time_list[iteration]

    # 初始化边缘节点数量
    node_num = settings.BASE_STATION_NUM + settings.RSU_NUM + settings.EDGE_VEHICLE_NUM
    fixed_node_num = settings.BASE_STATION_NUM + settings.RSU_NUM
    mobile_node_num = settings.EDGE_VEHICLE_NUM

    # 初始化激励值集合
    max_potential_value = np.zeros(len(fixed_edge_node) + len(edge_vehicle_node))

    # 初始化可用信道
    useful_channel_under_node = []
    for i in range(settings.BASE_STATION_NUM):
        useful_channel_under_node.append(
            init_useful_channel(settings.NODE_TYPE_BASE_STATION, i, fixed_edge_node, edge_vehicle_node))
    for i in range(settings.BASE_STATION_NUM, fixed_node_num):
        useful_channel_under_node.append(
            init_useful_channel(settings.NODE_TYPE_RSU, i, fixed_edge_node, edge_vehicle_node))
    for i in range(settings.EDGE_VEHICLE_NUM):
        useful_channel_under_node.append(
            init_useful_channel(settings.NODE_TYPE_VEHICLE, i, fixed_edge_node, edge_vehicle_node))

    # 初始化每个节点下的任务
    task_id_under_each_node_list = []
    for i in tqdm(range(settings.BASE_STATION_NUM)):
        print_to_console("初始化每个节点下的任务 BASE_STATION " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_BASE_STATION,
                                                              node_id=i,
                                                              distance_matrix=fixed_distance_matrix)

        task_id_under_each_node_list.append(task_id_under_edge_node)

    for i in tqdm(range(settings.RSU_NUM)):
        print_to_console("初始化每个节点下的任务 RSU " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_RSU,
                                                              node_id=i,
                                                              distance_matrix=fixed_distance_matrix)
        task_id_under_each_node_list.append(task_id_under_edge_node)

    for i in tqdm(range(settings.EDGE_VEHICLE_NUM)):
        print_to_console("初始化每个节点下的任务 EDGE_VEHICLE " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_VEHICLE,
                                                              node_id=i,
                                                              distance_matrix=mobile_distance_matrix)
        task_id_under_each_node_list.append(task_id_under_edge_node)

    # 初始化节点当前可用信道列表
    usable_channel_of_all_nodes = []
    for i in tqdm(range(settings.BASE_STATION_NUM)):
        print_to_console("初始化节点当前可用信道列表 BASE_STATION " + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[i])
        usable_channel_of_all_nodes.append(usable_channel)

    for i in tqdm(range(settings.RSU_NUM)):
        print_to_console("初始化节点当前可用信道列表 RSU " + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[settings.BASE_STATION_NUM + i])
        usable_channel_of_all_nodes.append(usable_channel)

    for i in tqdm(range(settings.EDGE_VEHICLE_NUM)):
        print_to_console("初始化节点当前可用信道列表 EDGE_VEHICLE " + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[fixed_node_num + i])
        usable_channel_of_all_nodes.append(usable_channel)

    # 初始化策略空间
    strategy_space_of_all_nodes = []
    for i in tqdm(range(settings.BASE_STATION_NUM)):
        print_to_console("初始化策略空间 BASE_STATION " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_BASE_STATION,
            node_id=i,
            distance_matrix_list=fixed_distance_matrix_list,
            task_list=task_list)
        strategy_list = generator_of_strategy_list(usable_channel_list=usable_channel_of_all_nodes[i],
                                                   task_id_under_edge_node=task_id_under_each_node_list[i],
                                                   task_time_limitation_under_edge_node=task_time_limitation_under_edge_node)
        strategy_space_of_all_nodes.append(strategy_list)

    for i in tqdm(range(settings.RSU_NUM)):
        print_to_console("初始化策略空间 RSU " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_RSU,
            node_id=i,
            distance_matrix_list=fixed_distance_matrix_list,
            task_list=task_list)
        strategy_list = generator_of_strategy_list(
            usable_channel_list=usable_channel_of_all_nodes[settings.BASE_STATION_NUM + i],
            task_id_under_edge_node=task_id_under_each_node_list[settings.BASE_STATION_NUM + i],
            task_time_limitation_under_edge_node=task_time_limitation_under_edge_node)
        strategy_space_of_all_nodes.append(strategy_list)

    for i in tqdm(range(settings.EDGE_VEHICLE_NUM)):
        print_to_console("初始化策略空间 EDGE_VEHICLE " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_VEHICLE,
            node_id=i,
            distance_matrix_list=mobile_distance_matrix_list,
            task_list=task_list)
        strategy_list = generator_of_strategy_list(
            usable_channel_list=usable_channel_of_all_nodes[settings.BASE_STATION_NUM + i],
            task_id_under_edge_node=task_id_under_each_node_list[fixed_node_num + i],
            task_time_limitation_under_edge_node=task_time_limitation_under_edge_node)
        strategy_space_of_all_nodes.append(strategy_list)

    # 初始化选择概率
    strategy_selection_probability_of_all_node = []
    for strategy_space in strategy_space_of_all_nodes:
        strategy_list_length = len(strategy_space)
        strategy_selection_probability = generator_of_strategy_selection_probability(strategy_list_length)
        strategy_selection_probability_of_all_node.append(strategy_selection_probability)

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
