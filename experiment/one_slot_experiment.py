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

import h5py
import numpy as np
import multiprocessing
from pathlib import Path
import pickle
from config.config import settings
from algorithm.IPUSS import weighted_choice, compute_task_is_finished, \
    compute_task_transmission_data, compute_potential_value, compute_probability_update_value, \
    compute_updated_probability, constructor_of_strategy, decimal2xBase
from experiment.experiment_save_and_reload import load_experiment_median_from_pickle
from tqdm import tqdm


def print_to_console(msg, objective=None):
    print("*" * 32)
    print(msg)
    if objective is not None:
        print(objective)
        print(type(objective))


def process_choose_strategy(i, strategy_selection_probability_dict, combination_and_strategy_length_of_all_nodes):
    if str(i) in strategy_selection_probability_dict.keys():
        strategy_no = weighted_choice(strategy_selection_probability_dict[str(i)])
        strategy = constructor_of_strategy(x_base_num=
                                           decimal2xBase(decimal_num=strategy_no,
                                                         x_base=combination_and_strategy_length_of_all_nodes[
                                                             i]["length_of_combination"][0]),
                                           combination_and_strategy_length=
                                           combination_and_strategy_length_of_all_nodes[i])
        return {"i": i,
                "strategy": strategy,
                "strategy_no": strategy_no}


def process_compute_task_transmission_data(i,
                                           task_id_under_each_node_list,
                                           selected_strategy,
                                           node_type,
                                           fixed_edge_node,
                                           edge_vehicle_node,
                                           useful_channel_under_node,
                                           fixed_node_num,
                                           fixed_distance_matrix,
                                           mobile_distance_matrix):
    if str(i) in selected_strategy.keys():
        # settings.NODE_TYPE_FIXED
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
        return {"i": i,
                "task_transmission_data": task_transmission_data}


if __name__ == '__main__':

    pickle_file = Path(load_experiment_median_from_pickle(3))
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

    # 开始单次时间片实验
    processes_number = 5
    # experiment_iteration_max = 10e5
    experiment_iteration_max = 100
    learning_rate = settings.LEARNING_RATE
    pbar = tqdm(total=100)

    h5py_file = h5py.File(settings.H5PY_FILE, "r+")
    strategy_selection_probability_dict = dict()
    for i in range(node_num):
        if str(i) in h5py_file.keys():
            strategy_selection_probability_dict[str(i)] = h5py_file[str(i)][:]

    while iteration < experiment_iteration_max:
        """
          ————————————————————————————————————————————————————————————————————————————————————
              单次迭代
          ————————————————————————————————————————————————————————————————————————————————————
        """
        print_to_console("第" + str(iteration) + "迭代开始")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if "iteration" in h5py_file.keys():
            del h5py_file["iteration"]
        h5py_file.create_dataset("iteration", data=iteration)
        if iteration == 0:
            # 随机选择策略
            print_to_console("迭代" + str(iteration) + " 随机选择策略")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            selected_strategy = dict()
            selected_strategy_no = dict()

            """
            ————————————————————————————————————————————————————————————————————————————————————
                 多线程运行 选择策略
            ———————————————————————————————————————————————————————————————————————————————————— 
            """
            pool_choose_strategy = multiprocessing.Pool(processes=processes_number)
            jobs_choose_strategy = []
            for i in tqdm(range(node_num)):
                jobs_choose_strategy.append(
                    pool_choose_strategy.apply_async(
                        process_choose_strategy,
                        (i, strategy_selection_probability_dict, combination_and_strategy_length_of_all_nodes)))
            for job in jobs_choose_strategy:
                result = job.get()
                selected_strategy[str(result["i"])] = result["strategy"]
                selected_strategy_no[str(result["i"])] = result["strategy_no"]

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
            for i in tqdm(range(fixed_node_num)):
                jobs_compute_task_data.append(
                    pool_compute_task_data.apply_async(
                        process_compute_task_transmission_data, (i,
                                                                 task_id_under_each_node_list,
                                                                 selected_strategy,
                                                                 node_type,
                                                                 fixed_edge_node,
                                                                 edge_vehicle_node,
                                                                 useful_channel_under_node,
                                                                 fixed_node_num,
                                                                 fixed_distance_matrix,
                                                                 mobile_distance_matrix)
                    )
                )

            node_type = settings.NODE_TYPE_MOBILE
            for i in tqdm(range(fixed_node_num, node_num)):
                jobs_compute_task_data.append(
                    pool_compute_task_data.apply_async(
                        process_compute_task_transmission_data, (i,
                                                                 task_id_under_each_node_list,
                                                                 selected_strategy,
                                                                 node_type,
                                                                 fixed_edge_node,
                                                                 edge_vehicle_node,
                                                                 useful_channel_under_node,
                                                                 fixed_node_num,
                                                                 fixed_distance_matrix,
                                                                 mobile_distance_matrix)
                    )
                )

            for job in jobs_compute_task_data:
                result = job.get()
                task_transmission_data_dict_of_all_nodes[str(result["i"])] = result["task_transmission_data"]

            finished = compute_task_is_finished(task_list=task_list,
                                                task_transmission_data_dict_of_all_nodes=
                                                task_transmission_data_dict_of_all_nodes)

            print_to_console("迭代" + str(iteration) + " 初始化最大策略值")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for i in range(node_num):
                if len(task_id_under_each_node_list[i]) != 0:
                    potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
                    # 初始化最大的策略值
                    max_potential_value[i] = potential_value

            print_to_console("迭代" + str(iteration) + " 结束")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            # 随机选择策略
            print_to_console("迭代" + str(iteration) + " 随机选择策略")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            selected_strategy = dict()
            selected_strategy_no = dict()

            """
            ————————————————————————————————————————————————————————————————————————————————————
                多线程运行 选择策略
            ———————————————————————————————————————————————————————————————————————————————————— 
            """
            pool_choose_strategy = multiprocessing.Pool(processes=processes_number)
            jobs_choose_strategy = []
            for i in tqdm(range(node_num)):
                jobs_choose_strategy.append(
                    pool_choose_strategy.apply_async(
                        process_choose_strategy,
                        (i, strategy_selection_probability_dict, combination_and_strategy_length_of_all_nodes)))
            for job in jobs_choose_strategy:
                result = job.get()
                selected_strategy[str(result["i"])] = result["strategy"]
                selected_strategy_no[str(result["i"])] = result["strategy_no"]

            # 计算激励值
            """
            ——————————————————————————————————————————————————————————————————————————————————
                多进程运行 计算传输数据量
            ——————————————————————————————————————————————————————————————————————————————————
            """
            pool_compute_task_data = multiprocessing.Pool(processes=processes_number)
            jobs_compute_task_data = []

            node_type = settings.NODE_TYPE_FIXED
            for i in tqdm(range(fixed_node_num)):
                jobs_compute_task_data.append(
                    pool_compute_task_data.apply_async(
                        process_compute_task_transmission_data, (i,
                                                                 task_id_under_each_node_list,
                                                                 selected_strategy,
                                                                 node_type,
                                                                 fixed_edge_node,
                                                                 edge_vehicle_node,
                                                                 useful_channel_under_node,
                                                                 fixed_node_num,
                                                                 fixed_distance_matrix,
                                                                 mobile_distance_matrix)
                    )
                )

            node_type = settings.NODE_TYPE_MOBILE
            for i in tqdm(range(fixed_node_num, node_num)):
                jobs_compute_task_data.append(
                    pool_compute_task_data.apply_async(
                        process_compute_task_transmission_data, (i,
                                                                 task_id_under_each_node_list,
                                                                 selected_strategy,
                                                                 node_type,
                                                                 fixed_edge_node,
                                                                 edge_vehicle_node,
                                                                 useful_channel_under_node,
                                                                 fixed_node_num,
                                                                 fixed_distance_matrix,
                                                                 mobile_distance_matrix)
                    )
                )

            for job in jobs_compute_task_data:
                result = job.get()
                task_transmission_data_dict_of_all_nodes[str(result["i"])] = result["task_transmission_data"]

            finished = compute_task_is_finished(task_list=task_list,
                                                task_transmission_data_dict_of_all_nodes=
                                                task_transmission_data_dict_of_all_nodes)
            # 计算激励值并更新策略选择概率
            print_to_console("迭代" + str(iteration) + " 计算激励值并更新策略选择概率")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            for i in range(node_num):
                if str(i) in selected_strategy_no.keys():
                    potential_value = compute_potential_value(task_id_under_each_node_list[i], finished)
                    probability_update_value = compute_probability_update_value(potential_value=potential_value,
                                                                                max_potential_value=max_potential_value[
                                                                                    i])
                    strategy_list = strategy_selection_probability_dict[str(i)]
                    origin_probability = strategy_list[selected_strategy_no[str(i)]]
                    new_probability = compute_updated_probability(origin_probability, learning_rate,
                                                                  probability_update_value)
                    strategy_selection_probability_dict[str(i)][selected_strategy_no[str(i)]] = new_probability
                    max_potential_value[i] = max(potential_value, max_potential_value[i])

        pbar.update(0.001)
        iteration += 1
