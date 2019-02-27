import csv
import json

import certifi
from urllib3 import PoolManager, Timeout
from urllib3.exceptions import TimeoutError,MaxRetryError
from urllib.parse import quote
from bs4 import BeautifulSoup
import multiprocessing as mp
from numpy.core.multiarray import ndarray
import numpy
from numpy.core.multiarray import ndarray
from typing import List
from random import randint
import time

class OlgasLibs:
    TIMEOUT = Timeout(connect=100.0, read=100.0)
    http = PoolManager(maxsize=10, timeout=TIMEOUT, retries=10, ca_certs=certifi.where())

    @classmethod
    def smartOpenHtml(cls, url, auth_token=None, reconnect_attempts_count=0):
        random_index = randint(0, 4)

        if not url:
            return ""
        else:
            try:
                print("Opening URL: " + url)
                headers_selection = [
                    {'User-Agent': 'Mozilla/5.0'},
                    {'User-Agent': 'Chrome/42.0.2311.90'},
                    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'},
                    {'User-Agent': 'AppleWebKit/537.36'},
                    {'User-Agent': 'Safari/537.36'}
                ]
                headers = headers_selection[random_index]

                if auth_token is not None: headers["Authorization"] = auth_token

                resp = cls.http.request("GET", url, headers=headers)
                searchResultsHtml = resp.data.decode('utf-8')
                resultsPage = BeautifulSoup(searchResultsHtml, 'html.parser')
                return resultsPage
            except TimeoutError as toe:
                print("Timeout reached attempting to connect to: " + url)
                print("Exception trace:".format(toe))
                print("reconnecting...")
                if (reconnect_attempts_count > cls.http.retries):
                    print("Max number of reconnection attempts reached: " + str(cls.http.retries))
                    print("Exception trace:".format(toe))
                    raise
                else:
                    cls.openHtml(url, reconnect_attempts_count + 1)
            except Exception as ex:
                print("Exception happened opening url: "+url)
                print(format(ex))
                raise

    @classmethod
    def openHtml(cls, url, auth_token=None, reconnect_attempts_count=0):

        if not url:
            return ""
        else:
            try:
                print("Opening URL: " + url)
                #headers = {'User-Agent': 'Mozilla/5.0'}
                headers = {'User-Agent': 'Chrome/42.0.2311.90 Safari/537.36'}

                if auth_token is not None: headers["Authorization"] = auth_token

                resp = cls.http.request("GET", url, headers=headers)
                searchResultsHtml = resp.data.decode('utf-8')
                resultsPage = BeautifulSoup(searchResultsHtml, 'html.parser')
                return resultsPage
            except TimeoutError as toe:
                print("Timeout reached attempting to connect to: " + url)
                print("Exception trace:".format(toe))
                print("reconnecting...")
                if (reconnect_attempts_count > cls.http.retries):
                    print("Max number of reconnection attempts reached: " + str(cls.http.retries))
                    print("Exception trace:".format(toe))
                    raise
                else:
                    cls.openHtml(url, reconnect_attempts_count + 1)

            except MaxRetryError:
                print("MaxRetryError")
                print("Reconnecting...")
                if (reconnect_attempts_count > cls.http.retries):
                    raise
                else:
                    time.sleep(100)
                    cls.openHtml(url, reconnect_attempts_count + 1)
            except Exception as ex:
                print("Exception happened opening url: "+url)
                print(format(ex))
                raise

    @classmethod
    def get_json(cls, url, headers={'User-Agent': 'Mozilla/5.0', "Accept-Language": "en-us"},
                 reconnect_attempts_count=0):

        TIMEOUT = Timeout(connect=10.0, read=10.0)
        http = PoolManager(maxsize=10, timeout=TIMEOUT, retries=10, ca_certs=certifi.where())

        if not url:
            return ""
        else:
            try:
                print("Opening URL: " + url)
                req = http.request("GET", url, headers={'User-Agent': 'Mozilla/5.0', "Accept-Language": "en-us"})
                respStr = req.data.decode('utf-8')
                jsonObj = json.loads(respStr)
                return jsonObj
            except TimeoutError as toe:
                print("Timeout reached attempting to connect to: " + url)
                print("Exception trace:".format(toe))
                print("reconnecting...")
                if (reconnect_attempts_count > http.retries):
                    print("Max number of reconnection attempts reached: " + str(http.retries))
                    print("Exception trace:".format(toe))
                    raise
                else:
                    cls.get_json(url, reconnect_attempts_count + 1)
            except Exception as err:
                print("Exception happened: ".format(err))
                raise

    @classmethod
    def get_url(cls, baseUrl, query_params={}):
        if len(query_params) is 0:
            return baseUrl
        else:
            first_param_pair = quote(query_params[0]) + "=" + quote(query_params[query_params[0]])
            url = baseUrl + "?" + first_param_pair
            params = []
            for param in query_params:
                url.append("&" + quote(param) + "=" + quote(params[param]))

            return url


    @classmethod
    def append_objects_to_csv_file(cls, path, objects, fieldnames=None):
        object_dics = []
        for object in objects:
            object_dics.append(object.__dict__)

        cls.append_to_csv_file(path,object_dics)

    @classmethod
    def append_to_csv_file(cls, path, data, fieldnames=None):
        if fieldnames is None and data is not None and len(data) > 0:
            fieldnames = data[0].keys()

        with open(path, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            #writer.writeheader()
            for entry in data:
                writer.writerow(entry)
        print("data appended to " + path)

    @classmethod
    def save_objects_to_csv_file(cls, path, objects, fieldnames=None):
        object_dics = []
        for object in objects:
            object_dics.append(object.__dict__)

        cls.save_to_csv_file(path,object_dics)


    @classmethod
    def save_to_csv_file(cls, path, data, fieldnames=None):
        if fieldnames is None and data is not None and len(data) > 0:
            fieldnames = data[0].keys()

        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)
        print("data saved to " + path)

    @classmethod
    def parallelise(cls, params, num_of_chunks, funct):

        chunks = numpy.array_split(params, num_of_chunks)
        output = mp.Queue()

        # self, song_ids: list, author_name: str, process_id:str, total_songs:int, output: Queue
        processes = [mp.Process(target=funct,
                                args=(chunk, output)) for chunk in chunks]
        for p in processes:
            p.start()

        for p in processes:
            p.join()

        results = []
        for p in processes:
            results.append(output.get())

        # Exit the completed processes

        return cls.flatten(results)

    @classmethod
    def get_optional(self, js, element_name, default_return=""):
        try:
            if js[element_name] is not None:
                return js[element_name]
            else:
                return default_return
        except KeyError as err:
            print("KeyError occurred with element_name: " + element_name)
            return default_return
        except TypeError as err:
            print("Type error occurred with element_name: " + element_name)
            return default_return

    @classmethod
    def flatten(cls, lst: List[List[str]]):
        sl = []
        for ss in lst:
            for a_song in ss:
                sl.append(a_song)
        return sl

