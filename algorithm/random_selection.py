#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   random_selection.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/29 下午5:11   neardws      1.0         None
"""
import random


def random_selection_strategy(combinations_in_list, length):
    """
    :argument
        combination_in_list: 所有行策略的排列组合
        length: 信道数量，均为10
    :return
        strategy_list: 所有节点的策略
    """
    strategy_list = []
    for combination in combinations_in_list:
        strategy = []
        for i in range(length):
            random_num = random.randint(0, len(combination) - 1)
            strategy.append(combination[random_num])
        strategy_list.append(strategy)
    return strategy_list
