#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   config.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/7/29 下午4:06   neardws      1.0         None
"""


from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.py', '.secrets.toml'],
)

