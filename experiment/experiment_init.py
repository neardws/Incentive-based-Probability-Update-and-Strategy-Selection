#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   experiment_init.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/31 下午4:35   neardws      1.0         None
"""
import pickle
from datetime import datetime
from pathlib import Path
import numpy as np

from algorithm.IPUSS import init_useful_channel, get_usable_channel_list, generator_of_strategy_list, \
    generator_of_strategy_selection_probability
from config.config import settings
from experiment.experiment_save_and_reload import save_experiment_median_to_pickle
from init_input.experiment_input_save_and_reload import load_pickle
from init_input.init_distance import get_task_id_under_edge_node, get_task_time_limitation_under_edge_node


def print_to_console(msg, objective=None):
    print("*" * 32)
    print(msg)
    if objective is not None:
        print(objective)
        print(type(objective))


if __name__ == '__main__':
    # TODO DEBUG

    # 读取实验参数设置
    # fixed_edge_node = None
    # edge_vehicle_node = None
    # task_by_time_list = None
    # fixed_distance_matrix_list = None
    # mobile_distance_matrix_list = None

    pickle_file = Path(load_pickle(7))
    # with pickle_file.open("rb") as fp:

    fp = pickle_file.open("rb")
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
    for i in range(settings.RSU_NUM):
        useful_channel_under_node.append(
            init_useful_channel(settings.NODE_TYPE_RSU, i, fixed_edge_node, edge_vehicle_node))
    for i in range(settings.EDGE_VEHICLE_NUM):
        useful_channel_under_node.append(
            init_useful_channel(settings.NODE_TYPE_VEHICLE, i, fixed_edge_node, edge_vehicle_node))

    # 初始化每个节点下的任务
    task_id_under_each_node_list = []
    for i in range(settings.BASE_STATION_NUM):
        print_to_console("初始化每个节点下的任务 BASE_STATION " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_BASE_STATION,
                                                              node_id=i,
                                                              distance_matrix=fixed_distance_matrix)

        task_id_under_each_node_list.append(task_id_under_edge_node)

    for i in range(settings.RSU_NUM):
        print_to_console("初始化每个节点下的任务 RSU " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_RSU,
                                                              node_id=i,
                                                              distance_matrix=fixed_distance_matrix)
        task_id_under_each_node_list.append(task_id_under_edge_node)

    for i in range(settings.EDGE_VEHICLE_NUM):
        print_to_console("初始化每个节点下的任务 EDGE_VEHICLE " + str(i))
        task_id_under_edge_node = get_task_id_under_edge_node(node_type=settings.NODE_TYPE_VEHICLE,
                                                              node_id=i,
                                                              distance_matrix=mobile_distance_matrix)
        task_id_under_each_node_list.append(task_id_under_edge_node)

    # 显示节点下所有任务的覆盖情况
    union_set = set()
    for i, task_id_under_edge_node in enumerate(task_id_under_each_node_list):
        union_set = union_set | set(task_id_under_edge_node)
    print("显示节点下所有任务的覆盖情况")
    print(union_set)
    print(len(union_set))

    # 初始化节点当前可用信道列表
    usable_channel_of_all_nodes = []
    for i in range(settings.BASE_STATION_NUM):
        print_to_console('初始化节点当前可用信道列表 BASE_STATION ' + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[i])
        usable_channel_of_all_nodes.append(usable_channel)

    for i in range(settings.RSU_NUM):
        print_to_console("初始化节点当前可用信道列表 RSU " + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[settings.BASE_STATION_NUM + i])
        usable_channel_of_all_nodes.append(usable_channel)

    for i in range(settings.EDGE_VEHICLE_NUM):
        print_to_console("初始化节点当前可用信道列表 EDGE_VEHICLE " + str(i))
        usable_channel = get_usable_channel_list(useful_channel_under_node[fixed_node_num + i])
        usable_channel_of_all_nodes.append(usable_channel)

    # 初始化任务的时间限制
    task_time_limitation_of_all_nodes = []
    for i in range(settings.BASE_STATION_NUM):
        print_to_console("初始化任务的时间限制 BASE_STATION " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_BASE_STATION,
            node_id=i,
            distance_matrix_list=fixed_distance_matrix_list,
            task_list=task_list)
        task_time_limitation_of_all_nodes.append(task_time_limitation_under_edge_node)

    for i in range(settings.RSU_NUM):
        print_to_console("初始化任务的时间限制 RSU " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_RSU,
            node_id=i,
            distance_matrix_list=fixed_distance_matrix_list,
            task_list=task_list)
        task_time_limitation_of_all_nodes.append(task_time_limitation_under_edge_node)

    for i in range(settings.EDGE_VEHICLE_NUM):
        print_to_console("初始化任务的时间限制 EDGE_VEHICLE " + str(i))
        task_time_limitation_under_edge_node = get_task_time_limitation_under_edge_node(
            node_type=settings.NODE_TYPE_VEHICLE,
            node_id=i,
            distance_matrix_list=mobile_distance_matrix_list,
            task_list=task_list)
        task_time_limitation_of_all_nodes.append(task_time_limitation_under_edge_node)

    # 初始化策略空间
    strategy_space_of_all_nodes = []
    for i in range(settings.BASE_STATION_NUM):
        print_to_console("初始化策略空间 BASE_STATION " + str(i))
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        strategy_list = generator_of_strategy_list(usable_channel_list_len=len(usable_channel_of_all_nodes[i]),
                                                   task_id_under_edge_node_len=len(task_id_under_each_node_list[i]),
                                                   time_limitation_under_edge_node=
                                                   task_time_limitation_of_all_nodes[i])
        strategy_space_of_all_nodes.append(strategy_list)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    for i in range(settings.RSU_NUM):
        print_to_console("初始化策略空间 RSU " + str(i))
        strategy_list = generator_of_strategy_list(
            usable_channel_list_len=len(usable_channel_of_all_nodes[settings.BASE_STATION_NUM + i]),
            task_id_under_edge_node_len=len(task_id_under_each_node_list[settings.BASE_STATION_NUM + i]),
            time_limitation_under_edge_node=task_time_limitation_of_all_nodes[settings.BASE_STATION_NUM + i])
        strategy_space_of_all_nodes.append(strategy_list)

    for i in range(settings.EDGE_VEHICLE_NUM):
        print_to_console("初始化策略空间 EDGE_VEHICLE " + str(i))
        strategy_list = generator_of_strategy_list(
            usable_channel_list_len=len(usable_channel_of_all_nodes[fixed_node_num + i]),
            task_id_under_edge_node_len=(task_id_under_each_node_list[fixed_node_num + i]),
            time_limitation_under_edge_node=task_time_limitation_of_all_nodes[fixed_node_num + i])
        strategy_space_of_all_nodes.append(strategy_list)

    # 初始化选择概率
    strategy_selection_probability_of_all_node = []
    for strategy_space in strategy_space_of_all_nodes:
        strategy_list_length = len(strategy_space)
        strategy_selection_probability = generator_of_strategy_selection_probability(strategy_list_length)
        strategy_selection_probability_of_all_node.append(strategy_selection_probability)

    save_success = save_experiment_median_to_pickle(iteration,
                                                    fixed_distance_matrix,
                                                    mobile_distance_matrix,
                                                    task_list,
                                                    node_num,
                                                    fixed_node_num,
                                                    mobile_node_num,
                                                    max_potential_value,
                                                    useful_channel_under_node,
                                                    task_id_under_each_node_list,
                                                    usable_channel_of_all_nodes,
                                                    task_time_limitation_of_all_nodes,
                                                    strategy_space_of_all_nodes,
                                                    strategy_selection_probability_of_all_node)
    if save_success:
        print("保存实验中间值成功")