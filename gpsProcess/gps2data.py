#!./venv python
# -*- encoding: utf-8 -*-
"""
@File    :   gps2data.py    
@Contact :   neard.ws@gmail.com
@Github  :   neardws

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/7/29 下午4:09   neardws      1.0         None

# time setup
    # 1 9AM
    # 2014/8/20 9:00 AM ----> 9:30 AM
    # 2 10PM
    # 2014/8/20 10:30 PM -----> 11:00 PM
    #
    # map setup
    # 1 3 x 3 KM
    # 中国四川省成都市武侯区武侯祠横街2号
    # latitude    30.646166   -----------> 30.676166
    # longitude   104.045824  -----------> 104.075824
    #
    # SELECT
    # 	*
    # FROM
    # 	`VehicleGPS`
    # WHERE
    # 	`timeStamp` >= '2014-08-20 09:00:00'
    # 	AND `timeStamp` <= '2014-08-20 09:30:00'
    # 	AND latitude >= 30.646166
    # 	AND latitude <= 30.676166
    # 	AND longitude >= 104.045824
    # 	AND longitude <= 104.075824

"""
from config.config import settings
import pymysql.cursors
import pandas as pd
import utm


def utm_get_relatively_coordinates(base_latitude, base_longitude, zone_length):
    """

    Args:
        base_latitude:
        base_longitude:
        zone_length:

    Returns:

    """
    utm_coordinate = utm.from_latlon(base_latitude, base_longitude)
    base_x = utm_coordinate[0]
    base_y = utm_coordinate[1]
    zone_number = utm_coordinate[2]
    zone_letter = utm_coordinate[3]
    relatively_x = base_x + zone_length
    relatively_y = base_y + zone_length
    return utm.to_latlon(relatively_x, relatively_y, zone_number, zone_letter)


def create_tempe_sql():
    # 连接数据库
    connect = pymysql.Connect(
        host=settings.host,
        port=settings.port,
        user=settings.username,
        passwd=settings.password,
        db=settings.database,
        charset='utf8'
    )

    # 根据坐标原点得到相对点的经纬度
    relatively_coordinates = utm_get_relatively_coordinates(settings.base_latitude,
                                                            settings.base_longitude,
                                                            settings.zone_length)
    relatively_latitude = relatively_coordinates[0]
    relatively_longitude = relatively_coordinates[1]


    #  获取游标
    cursor = connect.cursor()
    print("connect DB success")
    table_condition = "WHERE `timeStamp`>='" + settings.start_time + "'" \
                      "AND `timeStamp`<='" + settings.stop_time + "'" \
                      "AND latitude>=" + str(settings.base_latitude) + \
                      "AND latitude<=" + str(relatively_latitude) + \
                      "AND longitude>=" + str(settings.base_longitude) + \
                      "AND longitude<=" + str(relatively_longitude)
    sql_create_tem_table = "CREATE TEMPORARY TABLE tem_table SELECT * FROM VehicleGPS " + table_condition
    cursor.execute(sql_create_tem_table)
    print("create tem table success")
    return cursor


def sql_count(cursor):
    condition = " GROUP BY VehicleID"
    sql_query_vehicle_id = "SELECT VehicleID, COUNT(*) FROM tem_table " + condition
    cursor.execute(sql_query_vehicle_id)
    return cursor.fetchall()


def get_vehicle_id(points):  # 根据车辆出现的轨迹点数量来筛选车辆ID
    """

    Args:
        points:

    Returns:

    """
    vehicle_id = []
    sum = 0
    print("query time length success")
    for point in points:
        sum += point[1]
    print("SUM is " + str(len(points)))
    avg = sum / len(points)
    print("AVG is " + str(avg))
    i = 0
    num = 20
    for point in points:
        if point[1] >= num:  # value = 24
            i += 1
            vehicle_id.append(point[0])
    print("Number behind " + str(num) + " is " + str(i))
    return vehicle_id


def sql_info(info_cursor, info_id):
    """

    Args:
        info_cursor:
        info_id:

    Returns:

    """
    sql_query_vehicle_info = "SELECT latitude, longitude, " \
                             "TIMESTAMPDIFF(SECOND, '2014-08-20 09:00:00', timeStamp) FROM tem_table " \
                             + "WHERE VehicleID = " + str(info_id) + " ORDER BY timeStamp ASC"
    info_cursor.execute(sql_query_vehicle_info)
    return info_cursor.fetchall()


def get_vehicle_info(vehicle_ids, cursor):
    """

    Args:
        vehicle_ids:
        cursor:
    """
    base_id = 0
    for v_id in vehicle_ids:
        information = sql_info(info_cursor=cursor, info_id=v_id)
        # First node could be any time
        latitudes = []
        longitudes = []
        times = []
        for info in information:
            latitude = info[0]
            longitude = info[1]
            time = info[2]
            latitudes.append(latitude)
            longitudes.append(longitude)
            times.append(time)
            print(base_id, time, latitude, longitude)
        data_frame = pd.DataFrame({'id': base_id, 'time': times, 'latitude': latitudes, 'longitude': longitudes})
        if base_id == 0:
            data_frame.to_csv(settings.csv_name, index=False)
        else:
            data_frame.to_csv(settings.csv_name, mode='a', index=False, header=False)
        print("vehicleID" + str(base_id) + "complete")
        base_id += 1


if __name__ == '__main__':
    # 根据坐标原点得到相对点的经纬度
    relatively_coordinates = utm_get_relatively_coordinates(settings.base_latitude,
                                                            settings.base_longitude,
                                                            settings.zone_length)
    relatively_latitude = relatively_coordinates[0]
    relatively_longitude = relatively_coordinates[1]

    print(settings.base_latitude,settings.base_longitude)
    print(relatively_latitude,relatively_longitude)
