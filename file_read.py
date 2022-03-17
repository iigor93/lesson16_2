import json


def file_read(file_names):
    # read data from files
    file_name_users = file_names[0]
    file_name_orders = file_names[1]
    file_name_offers = file_names[2]

    with open(file_name_users) as file:
        users = json.load(file)
    with open(file_name_orders) as file:
        orders = json.load(file)
    with open(file_name_offers) as file:
        offers = json.load(file)

    return users, orders, offers
