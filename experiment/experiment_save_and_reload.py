#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   experiment_save_and_reload.py
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/31 下午4:14   neardws      1.0         None
"""

from datetime import *
import pickle
import random
from config.config import settings
from pathlib import Path


def get_median_unique_file_name():
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_number = random.randint(0, 100)  # 生成随机数n,其中0<=n<=100
    if random_number < 10:
        random_number = str(0) + str(random_number)
    unique_file_name = "../experiment_data/experiment_median/" + "Experiment_" + str(random_number) + "_" + str(
        now_time) + ".pkl"
    return unique_file_name


def save_experiment_median_to_pickle(iteration,
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
                                     combination_and_strategy_length_of_all_nodes
                                     ):
    file_name = get_median_unique_file_name()
    txt_file = Path(settings.EXPERIMENT_MEDIAN_FILE_NAME)
    with txt_file.open('a+', encoding='utf-8') as fp:
        fp.write(file_name + "\n")
    pickle_file = Path(file_name)
    with pickle_file.open("wb") as fp:
        pickle.dump(iteration, fp)
        pickle.dump(fixed_distance_matrix, fp)
        pickle.dump(mobile_distance_matrix, fp)
        pickle.dump(task_list, fp)
        pickle.dump(node_num, fp)
        pickle.dump(fixed_node_num, fp)
        pickle.dump(mobile_node_num, fp)
        pickle.dump(max_potential_value, fp)
        pickle.dump(useful_channel_under_node, fp)
        pickle.dump(task_id_under_each_node_list, fp)
        pickle.dump(usable_channel_of_all_nodes, fp)
        pickle.dump(task_time_limitation_of_all_nodes, fp)
        pickle.dump(combination_and_strategy_length_of_all_nodes, fp)
        return True


def load_experiment_median_from_pickle(input_number):
    json_file = Path(settings.EXPERIMENT_MEDIAN_FILE_NAME)
    file_name = ""
    with json_file.open('r', encoding="utf-8") as fp:
        file_lines = fp.readlines()
        print(file_lines)
        file_line = file_lines[input_number - 1]
        file_name = str(file_line).replace('\n', '')
    print(file_name)
    pickle_file = Path(file_name)
    if pickle_file.exists():
        return file_name
    else:
        raise FileNotFoundError("from init_input.experiment_input_save_and_reload Pickle File not found")


"""
保存迭代中间值
"""


# def get_iteration_unique_file_name():
#     now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     random_number = random.randint(0, 100)  # 生成随机数n,其中0<=n<=100
#     if random_number < 10:
#         random_number = str(0) + str(random_number)
#     unique_file_name = "../experiment_data/iteration_median/" + "Experiment_" + str(random_number) + "_" + str(
#         now_time) + ".pkl"
#     return unique_file_name


# def save_iteration_median_to_pickle(iteration,
#                                      learning_rate,
#                                      experiment_iteration_max,
#
#                                      ):
#     file_name = get_iteration_unique_file_name()
#     txt_file = Path(settings.ITERATION_MEDIAN_FILE_NAME)
#     with txt_file.open('a+', encoding='utf-8') as fp:
#         fp.write(file_name + "\n")
#     pickle_file = Path(file_name)
#     with pickle_file.open("wb") as fp:
#         pickle.dump(iteration, fp)
#
#         return True

#
# def load_iteration_median_from_pickle(input_number):
#     json_file = Path(settings.ITERATION_MEDIAN_FILE_NAME)
#     file_name = ""
#     with json_file.open('r', encoding="utf-8") as fp:
#         file_lines = fp.readlines()
#         print(file_lines)
#         file_line = file_lines[input_number - 1]
#         file_name = str(file_line).replace('\n', '')
#     print(file_name)
#     pickle_file = Path(file_name)
#     if pickle_file.exists():
#         return file_name
#     else:
#         raise FileNotFoundError("from init_input.experiment_input_save_and_reload Pickle File not found")



#
# if __name__ == '__main__':
#     # save_pickle()
#     # load_pickle(1)
