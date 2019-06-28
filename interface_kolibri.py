#!/usr/bin/env python

import requests
from time import sleep
import datetime
from pprint import pprint
from functools import wraps
import json
from urllib.parse import urljoin
import useful_utilities
import csv_db_funcs
import unittest.mock
import requests.models


def testable(func):
    """Wraps around classes allowing them to be run in 'test mode'

    Takes input as a function which when run in 'test-mode' returns sample
    output from a test file. This file is taken from the object's
    PATH_TO_SAMPLES_CSV file. By default discourse_interface takes this info
    from sampleresponse.csv. If TEST_MODE is False the function behaves normally

    :param func:
    :returns: A function which can be run in test mode by specifying TEST_MODE
    as True in the parent class
    :rtype: Function

    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            if self.TEST_MODE:
                sample = csv_db_funcs.identify(
                    "samples", func.__name__, self.PATH_TO_SAMPLES_CSV
                )
                if ((sample is None) or (sample == [])) and (
                    not self.TEST_MODE_DEFAULT_EMPTY
                ):
                    raise NotImplementedError(
                        "Add sample response for {} to {} or pass '{} = True' as an argument".format(
                            func.__name__, self.PATH_TO_SAMPLES_CSV, default_none_key
                        )
                    )
                else:
                    test_response = unittest.mock.Mock(spec=requests.models.Response)
                    test_response.content = json.dumps(sample).encode("utf-8")
                    test_response.status_code = 200
                    test_response.ok = True
                    test_response.json = lambda: sample
                    return self.parse_response(test_response)

            else:
                return func(self, *args, **kwargs)
        except KeyError as e:
            return func(self, *args, **kwargs)

    # wrapper = useful_utilities.debug_func(wrapper)
    return wrapper


ADMIN_NAME = "DUMMY_NAME"
API_KEY_GLOBAL = "DUMMY_KEY"


class kolibri_interface:
    def __init__(
        self,
        URL="http://localhost:8080",
        RETRIES=20,
        TEST_MODE=False,
        TEST_MODE_DEFAULT_EMPTY=False,
        QUIET_MODE=False,
        PATH_TO_SAMPLES_CSV="./sampleresponses.csv",
    ):
        for key, value in locals().items():
            setattr(self, key, value)
        self.LAST_RES = None

    def _request(
        self,
        _type,
        url,
        json,
        data,
        headers,
        files,
        params,
        timeout,
        allow_redirects,
        **kwargs
    ):
        """Primary requests endpoint. All requests must go through this instead

        :param _type: PUT, GET, POST, DELETE...type of request. (str)
        :param url:
        :param json:
        :param data:
        :param headers:
        :param files:
        :param params:
        :param timeout:
        :param allow_redirects:
        :returns: Response
        :rtype:

        """
        self.LAST_RES = None
        self.LAST_RQST = locals()
        for i in range(self.RETRIES):
            res = requests.request(
                _type,
                url,
                json=json,
                data=data,
                headers=headers,
                files=files,
                params=params,
                timeout=timeout,
                allow_redirects=allow_redirects,
                **kwargs
            )
            self.LAST_RES = res
            if res.status_code == 429:
                try:
                    time = res.json()["extras"]["wait_seconds"]
                except Exception as e:
                    time = 10
                if not self.QUIET_MODE:
                    pprint(res.content)
                    print("Waiting for throttle...")
                    print("Sleeping for {} seconds".format(time))
                sleep(int(time))
            else:
                return res

    def parse_response(self, response):
        """Checks the response code. Pprints the response content if everything went well.

        Checks if a standard response is returned. Usefull for logging.

        :param response: The response
        :returns: Response
        :rtype:

        """
        if self.QUIET_MODE:
            return response
        try:
            pprint(json.loads(response.content))
        except:
            pass
        if response.ok:
            print("Success!")
        elif response.status_code == 403:
            print("Access denied")
        elif response.status_code == 400:
            print("Missing Param/Invalid Request")
        elif response.status_code == 422:
            raise NotImplementedError
        else:
            print("Unknown Response")
            print(response.status_code)
        return response

    def get_request(
        self,
        data,
        url,
        files={},
        params={},
        json={},
        timeout=None,
        allow_redirects=True,
        **kwargs
    ):
        headers = {"Accept": "application/json; charset=utf-8"}
        response = self._request(
            "GET",
            url,
            json=json,
            data=data,
            headers=headers,
            files=files,
            params=params,
            timeout=timeout,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.parse_response(response)

    def delete_request(
        self,
        data,
        url,
        files={},
        params={},
        json={},
        timeout=None,
        allow_redirects=True,
        **kwargs
    ):
        headers = {"Accept": "application/json; charset=utf-8"}
        response = self._request(
            "DELETE",
            url,
            json=json,
            data=data,
            headers=headers,
            files=files,
            params=params,
            timeout=timeout,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.parse_response(response)

    def put_request(
        self,
        data,
        url,
        files={},
        params={},
        json={},
        timeout=None,
        allow_redirects=True,
        **kwargs
    ):
        headers = {"Accept": "application/json; charset=utf-8"}
        response = self._request(
            "PUT",
            url,
            json=json,
            data=data,
            headers=headers,
            files=files,
            params=params,
            timeout=timeout,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.parse_response(response)

    def post_request(
        self,
        data,
        url,
        files={},
        params={},
        json={},
        timeout=None,
        allow_redirects=True,
        **kwargs
    ):
        headers = {"Accept": "application/json; charset=utf-8"}
        # headers = {
        #     # "Accept": "application/json; charset=utf-8",
        #     "Content-Type":"multipart/form-data",
        #     "Api-Key": API_KEY,
        #     "Api-Username": API_USERNAME
        # }
        response = self._request(
            "POST",
            url,
            json=json,
            data=data,
            headers=headers,
            files=files,
            params=params,
            timeout=timeout,
            allow_redirects=allow_redirects,
            **kwargs
        )
        return self.parse_response(response)

    # @testable
    # def get_children(self, parent, user_kind="superuser"):
    #     end_point = "/api/content/contentnode_slim"
    #     url_with_end_point = urljoin(self.URL, end_point)
    #     data = locals()
    #     return self.get_request(data, url_with_end_point)

    @testable
    def get_channels(self, available=True):
        end_point = "/api/content/channel"
        url_with_end_point = urljoin(self.URL, end_point)
        data = dict()
        params = locals()
        return self.get_request(data, url_with_end_point, params=params)

    @testable
    def get_children(self, parent, user_kind="superuser"):
        end_point = "/api/content/contentnode_slim"
        url_with_end_point = urljoin(self.URL, end_point)
        data = dict()
        params = locals()
        return self.get_request(data, url_with_end_point, params=params)

    @testable
    def get_node_details(self, node):
        end_point = "/api/content/contentnode/{}".format(node)
        url_with_end_point = urljoin(self.URL, end_point)
        data = dict()
        return self.get_request(data, url_with_end_point)

    @testable
    def fetch_content(self, storage_url, save_at=None):
        url_with_end_point = urljoin(self.URL, storage_url)
        data = dict()
        res = self.get_request(data, url_with_end_point)
        if save_at is None:
            return res
        else:
            with open(save_at, "wb") as my_file:
                my_file.write(res.content)
            return res
