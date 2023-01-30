import socket
import json
import os

filepath = '/Users/shanmarsh/Downloads/data.json'  # File path of the file to be monitored
file = open(filepath)
initial_file_modified_time = os.path.getmtime(filepath)  # Get file modified time
initial_access_points = []


# function to act as a server to monitor the AP file, and sends encoded data to its clients connected
def server():
    host = '127.0.0.1'  # HostIP of Server running  || alternatively can use socket.gethostname() if localhost
    port = 5050  # Port of Server running

    exporter = socket.socket()
    exporter.bind((host, port))
    exporter.listen(5)  # No. of clients the server can listen simultaneously
    conn, address = exporter.accept()  # accept new connection

    while True:  # Ensure the application runs till interrupted manually
        if is_file_modified():
            read_file(conn)


# function to initiate the initial read of data.
def initial_setup():
    global initial_access_points
    initial_read = json.load(file)
    initial_access_points = get_access_points(initial_read)


# function to separate the values of access points as a JSON list.
def get_access_points(access_points):
    ap_data = {}
    for i in access_points['access_points']:
        ssid = i['ssid']
        i.pop('ssid')
        ap_data[ssid] = i
    return ap_data


# validate if the file is modified, before executing the application
def is_file_modified():
    global initial_file_modified_time
    file_modified_time = os.path.getmtime(filepath)
    if file_modified_time != initial_file_modified_time:
        initial_file_modified_time = os.path.getmtime(filepath)  # update to latest time modified time
        return True


def read_file(connection):
    global initial_access_points
    read = json.load(open(filepath))  # Read Json data from file
    access_points = get_access_points(read)

    # convert json data to set to compare list
    access_point_keys = set(access_points.keys())
    initial_access_point_keys = set(initial_access_points.keys())

    deleted_ap = sorted(initial_access_point_keys - access_point_keys)
    for ap in deleted_ap:
        connection.send(f'{ap} is removed from the list'.encode())

    added_ap = sorted(access_point_keys - initial_access_point_keys)
    for ap in added_ap:
        ap_data = access_points[ap]
        connection.send(
            f'{ap} is added to the list with SNR {ap_data["snr"]} and CHANNEL {ap_data["channel"]}'.encode())

    updated_ap = sorted(initial_access_point_keys & access_point_keys)
    for ap in updated_ap:
        prev_ap = initial_access_points[ap]
        curr_ap = access_points[ap]
        if prev_ap["snr"] != curr_ap["snr"]:
            connection.send(f'{ap}\'s SNR has from {prev_ap["snr"]} to {curr_ap["snr"]}'.encode())
        if prev_ap["channel"] != curr_ap["channel"]:
            connection.send(f'{ap}\'s Channel has from {prev_ap["channel"]} to {curr_ap["channel"]}'.encode())

    initial_access_points.clear()
    initial_access_points = access_points  # Update current data for next iteration


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    initial_setup()
    server()
