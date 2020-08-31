#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   experiment_input_save_and_reload.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 上午12:47   neardws      1.0         None
"""
import os
from datetime import *
import pickle
import random
from config.config import settings
from pathlib import Path


def get_unique_file_name():
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_number = random.randint(0, 100)  # 生成随机数n,其中0<=n<=100
    if random_number < 10:
        random_number = str(0) + str(random_number)
    unique_file_name = "../experiment_data/experiment_input/" + "Experiment_" + str(random_number) + "_" + str(now_time) + ".pkl"
    return unique_file_name


def save_pickle(fixed_edge_node,
                edge_vehicle_node,
                task_by_time_list,
                fixed_distance_matrix_list,
                mobile_distance_matrix_list):
    file_name = get_unique_file_name()
    txt_file = Path(settings.experiment_file_name)
    with txt_file.open('a+', encoding='utf-8') as fp:
        fp.write(file_name + "\n")
    pickle_file = Path(file_name)
    with pickle_file.open("wb") as fp:
        pickle.dump(fixed_edge_node, fp)
        pickle.dump(edge_vehicle_node, fp)
        pickle.dump(task_by_time_list, fp)
        pickle.dump(fixed_distance_matrix_list, fp)
        pickle.dump(mobile_distance_matrix_list, fp)
        return True


def load_pickle(input_number):
    json_file = Path(settings.experiment_file_name)
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
        # with pickle_file.open("rb") as fp:
        #     fixed_edge_node = pickle.load(fp)
        #     edge_vehicle_node = pickle.load(fp)
        #     task_by_time_list = pickle.load(fp)
        #     fixed_distance_matrix_list = pickle.load(fp)
        #     mobile_distance_matrix_list = pickle.load(fp)
    else:
        raise FileNotFoundError("from init_input.experiment_input_save_and_reload Pickle File not found")


if __name__ == '__main__':
    save_pickle()
    load_pickle(1)