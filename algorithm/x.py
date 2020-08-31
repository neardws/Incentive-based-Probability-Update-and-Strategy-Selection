#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   x.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/31 下午3:42   neardws      1.0         None
"""
import itertools
from datetime import datetime
import numpy as np
from tqdm import tqdm


def generator_of_strategy_list(usable_channel_list_len, task_id_under_edge_node_len, task_time_limitation_under_edge_node):

    strategy_list = []

    # x 轴，节点当前可用的信道
    x_length = usable_channel_list_len

    # y 轴, 节点的所有任务数
    y_length = task_id_under_edge_node_len

    if y_length != 0:

        j_strategy_list = [[0, 0]]

        for j in range(y_length):
            for k in range(int(task_time_limitation_under_edge_node[j])):
                j_strategy_list.append([j+1, k+1])
        print(j_strategy_list)
        print(len(j_strategy_list))

        for strategy in itertools.product(j_strategy_list, repeat=x_length):
            strategy_list.append(strategy)

        return strategy_list
    else:
        return


if __name__ == '__main__':
    task_time_limitation_under_edge_node = [1, 2, 1, 1]
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    strategy_list = generator_of_strategy_list(5, 4, task_time_limitation_under_edge_node)
    print(strategy_list[1])
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # exit()
    # # print(len(strategy_list))