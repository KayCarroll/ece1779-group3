import requests
import random
import time
import matplotlib.pyplot as plt
import numpy as np

#API_URL = "http://52.0.219.43:5001/"
API_URL = "http://127.0.0.1:5001/api"

def plot_graph(x_axis, put_results, get_results, plot_title, x_axis_label, y_axis_label, invert_x=False):
    pass

def get_list_of_keys(num_itesm = 1):
    result = []
    for i in range(num_itesm):
        result.append("test_" + str(i))
    return result

def test_latency(num_requests = 1, request_type = "put"):
    if request_type == "put":
        total_response_time = 0
        file_1 = {'file': open('./images/1.jpeg', 'rb')}
        list_of_items = get_list_of_keys(num_requests)
        for item in list_of_items:
            response_time = requests.post(API_URL + "/upload", files=file_1, data={'key': item}).elapsed.total_seconds()
            total_response_time += response_time
        return total_response_time/num_requests
    elif request_type == "get":
        total_response_time = 0
        list_of_items = get_list_of_keys(round(num_requests/4))
        list_of_items = list_of_items*4
        random.shuffle(list_of_items)
        for item in list_of_items:
            response_time = requests.post(API_URL + "/key/" + item).elapsed.total_seconds()
            total_response_time += response_time
        return total_response_time/num_requests
    else:
        print("Not a valid request type")

def test_throughput(num_seconds = 5, request_type = "put"):
    if request_type == "put":
        file_1 = {'file': open('./images/1.jpeg', 'rb')}
        total_throughput = 0
        t_end = time.time() + num_seconds
        list_of_items = get_list_of_keys(10000)
        i = 0
        while time.time() < t_end:
            requests.post(API_URL + "/upload", files=file_1, data={'key': list_of_items[i]})
            i += 1
            total_throughput += 1
        return total_throughput
    elif request_type == "get":
        total_throughput = 0
        t_end = time.time() + num_seconds
        list_of_items = get_list_of_keys(25)
        list_of_items = list_of_items * 4
        random.shuffle(list_of_items)
        i = 0
        while time.time() < t_end:
            if i >= len(list_of_items):
                i = 0
            requests.post(API_URL + "/key/" + list_of_items[i])
            i += 1
            total_throughput += 1
        return total_throughput
    else:
        print("Not a valid request type")

def constant_node_test(max_requests = 101, max_time = 25):
    print("########################### Benchmarking Constant MemCache Node Pool Size ##################")
    requests.post(f"{API_URL}/configure_cache?mode=manual&numNodes=4&cacheSize=1&policy=LRU")
    requests_test = range(1, max_requests, 10)
    total_time_elapsed = 0
    total_put_requests_processed = 0
    total_get_requests_processed = 0
    seconds_test = [0]
    latency_put_results = []
    latency_get_results = []
    throughput_put_results = [0]
    throughput_get_results = [0]
    for num_requests in requests_test:
        latency_put_results.append(test_latency(num_requests=num_requests, request_type="put"))
        latency_get_results.append(test_latency(num_requests=num_requests, request_type="get"))
    print("x_axis = " + str(requests_test))
    print("Constant_pool_latency_put_results = " + str(latency_put_results))
    print("Constant_pool_latency_get_results = " + str(latency_get_results))
    requests.post(API_URL + "/delete_all")
    fig1 = plt.figure("Constant Node Pool Latency Plot")
    plt.title("Constant Node Pool Latency vs. # of Repuests")
    plt.xlabel("Number of requests sent")
    plt.ylabel("Average response time (seconds)")
    plt.plot(requests_test, latency_put_results, 'o-', label = 'PUT requests')
    plt.plot(requests_test, latency_get_results, 'o-', label = 'GET requests')
    for x,y in zip(requests_test, latency_put_results):
        label = "{:.2f}".format(y)
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    for x,y in zip(requests_test, latency_get_results):
        label = "{:.2f}".format(y)
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    plt.legend()

    while total_time_elapsed <= max_time:
        total_put_requests_processed += test_throughput(num_seconds=5, request_type="put")
        total_get_requests_processed += test_throughput(num_seconds=5, request_type="get")
        total_time_elapsed += 5
        seconds_test.append(total_time_elapsed)
        throughput_put_results.append(total_put_requests_processed)
        throughput_get_results.append(total_get_requests_processed)
    print("x_axis = " + str(seconds_test))
    print("Constant_pool_throughput_put_results = " + str(throughput_put_results))
    print("Constant_pool_throughput_get_results = " + str(throughput_get_results))
    requests.post(API_URL + "/delete_all")
    fig2 = plt.figure("Constant Node Pool Throughput Plot")
    plt.title("Constant Node Pool throughput vs. time")
    plt.xlabel("Number of seconds elapsed")
    plt.ylabel("Requests served")
    plt.plot(seconds_test, throughput_put_results,'o-', label = 'PUT requests')
    plt.plot(seconds_test, throughput_get_results,'o-', label = 'GET requests')
    for x,y in zip(seconds_test, throughput_put_results):
        label = y
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    for x,y in zip(seconds_test, throughput_get_results):
        label = y
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    plt.legend()

def varying_memcache_test(start_node=1, end_node=8, num_requests=20, num_seconds=5):
    delta = end_node - start_node
    graph_type = "Growing"
    increment = 1
    if delta < 0:
        graph_type = "Shrinking"
        increment = -1
    print(f"########################### Benchmarking {graph_type} MemCache Node Pool Size Latency ##################")
    current_node = start_node
    requests.post(f"{API_URL}/configure_cache?mode=manual&numNodes={start_node}")
    # pre populate the system with 100 images
    #test_latency(num_requests=100, request_type='put')
    x_axis = []
    latency_put_results = []
    latency_get_results = []
    test_done = False
    while not test_done:
        if current_node == end_node:
            test_done = True
        latency_put_results.append(test_latency(num_requests=num_requests, request_type='put'))
        latency_get_results.append(test_latency(num_requests=num_requests, request_type='get'))
        x_axis.append(current_node)
        current_node += increment
        requests.post(f"{API_URL}/configure_cache?mode=manual&numNodes={current_node}")
    print("x axis = " + str(x_axis))
    print(f'{graph_type}_pool_latency_put_results = ' + str(latency_put_results))
    print(f'{graph_type}_pool_latency_get_results = ' + str(latency_get_results))
    fig1 = plt.figure(graph_type + " Node Pool Latency Plot")
    plt.title(graph_type + " Node Pool Latency vs. # of Active Nodes")
    plt.xlabel("Number of Active Nodes")
    plt.ylabel("Average response time (seconds)")
    plt.plot(x_axis, latency_put_results, 'o-', label = 'PUT requests')
    plt.plot(x_axis, latency_get_results, 'o-', label = 'GET requests')
    if delta < 0:
        plt.gca().invert_xaxis()
    for x,y in zip(x_axis, latency_put_results):
        label = "{:.2f}".format(y)
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    for x,y in zip(x_axis, latency_get_results):
        label = "{:.2f}".format(y)
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    plt.legend()

    print(f"########################### Benchmarking {graph_type} MemCache Node Pool Size Throughput ##################")

    throughput_put_results = []
    throughput_get_results = []
    test_done = False
    current_node = start_node
    requests.post(f"{API_URL}/configure_cache?mode=manual&numNodes={start_node}")
    while not test_done:
        if current_node == end_node:
            test_done = True
        throughput_put_results.append(test_throughput(num_seconds = num_seconds, request_type='put'))
        throughput_get_results.append(test_throughput(num_seconds = num_seconds, request_type='get'))
        current_node += increment
        requests.post(f"{API_URL}/configure_cache?mode=manual&numNodes={current_node}")

    print(f'{graph_type}_pool_throughput_put_results = ' + str(throughput_put_results))
    print(f'{graph_type}_pool_throughput_get_results = ' + str(throughput_get_results))
    fig2 = plt.figure(graph_type + " Node Pool Throughput Plot")
    plt.title(graph_type + " Node Pool Thoughput vs. # of Active Nodes")
    plt.xlabel("Number of Active Nodes")
    plt.ylabel("Throughput over 5 seconds")
    plt.plot(x_axis, throughput_put_results, 'o-', label = 'PUT requests')
    plt.plot(x_axis, throughput_get_results, 'o-', label = 'GET requests')
    if delta < 0:
        plt.gca().invert_xaxis()
    for x,y in zip(x_axis, throughput_put_results):
        label = y
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    for x,y in zip(x_axis, throughput_get_results):
        label = y
        plt.annotate(label, # this is the text
                    (x,y), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    plt.legend()


def test():
    ###########################
    # CONSTANT MEMCACHE NODE POOL SIZE
    ###########################
    constant_node_test(max_requests=101, max_time=25)
    varying_memcache_test(start_node=1, end_node=8)
    varying_memcache_test(start_node=8, end_node=1)
    plt.show()


if __name__ == "__main__":
    test()
    # varying_memcache_test(start_node=8, end_node=1)
    # plt.show()
    #test_latency(num_requests = 20, request_type = "put")



