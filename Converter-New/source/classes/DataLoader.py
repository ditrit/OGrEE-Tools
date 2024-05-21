from __future__ import annotations
import json
from typing import Any
from enum import Enum
from abc import ABC, abstractmethod
import typing
from source.Api import APIHandler
from functools import wraps


class EDCIM(Enum):
    NETBOX = 1
    DCTRACK = 2
    OGREE = 4


class DataLoader(ABC):
    edcim: EDCIM

    def __init__(self, api_url: str | None = None, api_headers: str | None = None) -> None:
        """
        The __init__ function is the constructor for the class. It initializes all of the instance variables to empty dictionaries, and sets up an APIHandler object if a URL was provided.

        :param api_url: str | None: Specify the url of the api
        :param api_headers: str | None: Set the headers for the apihandler
        :return: None
        """
        self.item_tree = dict()
        self.item_data = dict()
        self.model_tree = dict()
        self.model_data = dict()
        self.api_handler = APIHandler(api_url, api_headers) if api_url is not None else None

    def needs_connexion(func):
        @wraps(func)
        def wrapper(self: DataLoader, *args, **kwargs) -> Any:
            if self.api_handler is None:
                raise Exception(f"{func.__name__} : No URL provided")
            return func(self, *args, **kwargs)

        return wrapper

    @needs_connexion
    def get_data(self, endpoint: str, headers: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        The get_data function is a wrapper for the GetJSON function in the APIHandler class.
            It takes an endpoint and headers as arguments, and returns a dictionary of data from that endpoint.

        :param endpoint: str: Specify the endpoint of the api call
        :param headers: dict[str, Any]: Pass in the headers for the request
        :return: A dictionary with the data from the endpoint
        """
        return self.api_handler.GetJSON(headers, endpoint)

    @needs_connexion
    def post_data(self, endpoint: str, payload: dict[str, Any], headers: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        The post_data function is used to post data to the API.

        :param endpoint: str: Specify the endpoint that you want to send data to
        :param payload: dict[str, Any]: Pass the data to the endpoint
        :param headers: dict[str, Any] | None: Pass in the headers for the request
        :return: A dictionary with the data from the endpoint
        """
        return self.api_handler.PostJSON(headers, endpoint, payload)

    @needs_connexion
    def put_data(self, endpoint: str, payload: dict[str, Any], headers: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        The put_data function is used to send a PUT request to the specified endpoint.

        :param endpoint: str: Specify the endpoint of the api call
        :param payload: dict[str, Any] | None: Pass the data to be sent in the body of a request
        :param headers: dict[str, Any] | None: Pass the headers to the api call
        :return: A dictionary of the response
        """
        return self.api_handler.PutJSON(headers, endpoint, payload)

    @abstractmethod
    def get_all_items(self) -> None:
        pass

    @abstractmethod
    def get_all_models(self) -> None:
        pass

    @abstractmethod
    def get_one_item(self, name: str, category: str) -> None:
        pass

    @abstractmethod
    def get_one_model(self, name: str) -> None:
        pass

    @abstractmethod
    def get_one_manufacturer(self, name: str) -> None:
        pass

    @abstractmethod
    def add_item(self, fields: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def modify_item(self, fields: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def models(self, model_class: str, invert: bool = False) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_locations(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_racks(self, location: dict[str, Any]) -> dict[str, Any]:
        pass

    def import_from_json(self, file: typing.IO, model: bool) -> None:
        """
        The import_from_json function takes a file object and a boolean value.
        If the boolean is True, it will import the model data from the file into self.model_tree and self.model_data;
        if False, it will import item data into self.item_tree and self.item_data.

        :param file: typing.IO: Specify the file that is being read from
        :param model: bool: Determine whether the data being imported is for a model or an item
        :return: None
        """
        json_data = json.load(file)
        if model:
            self.model_tree = json_data["tree"]
            self.model_data = json_data["items"]
        else:
            self.item_tree = json_data["tree"]
            self.item_data = json_data["items"]
        file.close()

    def export_to_json(self, file: typing.IO, model: bool) -> None:
        """
        The export_to_json function takes a file object and a boolean value.
        The function then creates a dictionary with the keys "DCIM", "items", and "tree".
        The values of these keys are the name of the DCIM, either self.model_data or self.item_data,
        and either self.model_tree or self.item_tree respectively.

        :param file: typing.IO: Specify the file to be written to
        :param model: bool: Determine whether to export the model data or item data
        :return: None
        """
        json_data = {
            "DCIM": self.edcim.name,
            "items": self.model_data if model else self.item_data,
            "tree": self.model_tree if model else self.item_tree,
        }
        json.dump(json_data, file, indent=4)
        file.close()


class NetBoxDataLoader(DataLoader):
    edcim = EDCIM.NETBOX

    def find_key(self, key: Any) -> Any | None:
        """
        The find_key function takes a key and returns the value associated with that key.
        If the key is not found, it will return None.

        :param key: Any: Specify the key that is being searched for in the dictionary
        :return: The value of the key that is passed in
        """

        def aux(key: Any, dic: dict) -> Any | None:
            """
            The aux function is a recursive function that takes in a key and dictionary.
            It will return the value of the key if it exists in the dictionary, otherwise
            it will recursively search through all values of type dict until it finds
            the value or returns None.

            :param key: Any: Specify the key that is being searched for in the dictionary
            :param dic: dict: Specify the dictionary that is being passed into the function
            :return: The value of the key in the dictionary
            """
            if key in dic:
                return dic[key]
            for v in dic.values():
                if isinstance(v, dict):
                    res = aux(key, v)
                    if res is not None:
                        return res
            return None

        return aux(key, self.item_tree)

    def insert_item_and_parents(self, item : dict, root_level : dict) -> dict:
        """
        The insert_item_and_parents function takes an item and a root_level.
        If the item has a parent, it calls itself recursively with the parent as its first argument.
        It then inserts the current item into its parent's dictionary (or creates one if necessary).
        Finally, it returns that dictionary so that subsequent items can be inserted into it.

        :param item: The item data
        :param root_level: The top level of the dictionnary
        :return: The parent of the item
        """
        if "parent" in item and item["parent"] is not None:
            parent = self.insert_item_and_parents(item["parent"], root_level)
            if item["name"] not in parent:
                parent[item["name"]] = {}
            return parent[item["name"]]
        if item["name"] not in root_level:
            root_level[item["name"]] = {}
        return root_level[item["name"]]

    def get_all_items(self) -> None:
        """
        The get_all_items function gets all items from NetBox.
        It does this by first getting all regions, sites, locations, racks and devices from NetBox. Then it iterates over each item type
        and inserts them into their respective parents (if they have any). If an item has no parent then it will be inserted into the root.

        :return: None
        """
        regions = self.get_items("/api/dcim/regions?limit=0")
        sites = self.get_items("/api/dcim/sites?limit=0")
        locations = self.get_items("/api/dcim/locations?limit=0")
        racks = self.get_items("/api/dcim/racks?limit=0")
        devices = self.get_items("/api/dcim/devices?limit=0")
        powerports = self.get_items("/api/dcim/power-ports?limit=0")
        self.item_tree = {self.edcim.name: {}}
        self.item_data = {self.edcim.name: {}}

        for region in regions:
            self.insert_item_and_parents(region, self.item_tree[self.edcim.name])
            self.item_data[region["name"]] = region
        for site in sites:
            if "region" in site and site["region"] is not None:
                self.insert_item_and_parents(site, self.find_key(site["region"]["name"]))
            else:
                self.insert_item_and_parents(site, self.item_tree[self.edcim.name])
            self.item_data[site["name"]] = site
        for location in locations:
            self.insert_item_and_parents(location, self.find_key(location["site"]["name"]))
            self.item_data[location["name"]] = location
        for rack in racks:
            if "location" in rack and rack["location"] is not None:
                self.insert_item_and_parents(rack, self.find_key(rack["location"]["name"]))
            else:
                self.insert_item_and_parents(rack, self.find_key(rack["site"]["name"]))
            self.item_data[rack["name"]] = rack
        for device in devices:
            if "rack" in device and device["rack"] is not None:
                self.insert_item_and_parents(device, self.find_key(device["rack"]["name"]))
            elif "location" in device and device["location"] is not None:
                self.insert_item_and_parents(device, self.find_key(device["location"]["name"]))
            else:
                self.insert_item_and_parents(device, self.find_key(device["site"]["name"]))
            self.item_data[device["name"]] = device
        for powerport in powerports:
            device = self.item_data[powerport["device"]["name"]]
            if "powerports" not in device:
                device["powerports"] = []
            device["powerports"].append(powerport)

    def get_all_models(self) -> None:
        """
        The get_all_models function is used to populate the model_data and model_tree dictionaries from NetBox data.

        :return: None
        """
        data = self.get_items("/api/dcim/device-types?limit=0")
        for model in data:
            self.model_data[model["model"]] = model
            if model["manufacturer"]["name"] in self.model_tree:
                self.model_tree[model["manufacturer"]["name"]][model["model"]] = {}
            else:
                self.model_tree[model["manufacturer"]["name"]] = {model["model"]: {}}

    def get_one_model(self, name: str) -> None:
        """
        The get_one_model function takes a model name as an argument and gets its manufacter and its data from NetBox
        
        :param name: str: Specify the name of the model you want to get
        :return: None
        :doc-author: Trelent
        """
        model = self.get_items(f"/api/dcim/device-types?model={name}")[0]
        self.model_tree = {model["manufacturer"]["name"]: {model["model"]: {}}}
        self.model_data = {model["model"]: model}

    def get_one_manufacturer(self, name: str) -> None:
        """
        The get_one_manufacturer function takes a manufacturer name as an argument and gets the models data for that manufacturer from NetBox.

        :param name: str: Pass the name of the manufacturer to be searched for
        :return: None
        """
        data = self.get_items(f"/api/dcim/device-types?manufacturer={name.lower()}&limit=0")
        for model in data:
            self.model_data[model["model"]] = model
            if model["manufacturer"]["name"] in self.model_tree:
                self.model_tree[model["manufacturer"]["name"]][model["model"]] = {}
            else:
                self.model_tree[model["manufacturer"]["name"]] = {model["model"]: {}}

    def get_items(self, endpoint: str, headers: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        The get_items function is a recursive function that will continue to call itself until the next page of results is None.
        This allows us to get all items from an endpoint without having to worry about pagination.

        :param endpoint: str: Specify the endpoint to be used in the request
        :param headers: dict[str, Any] | None : Pass in the headers for the request
        :return: A dictionary
        """
        json_request = self.get_data(endpoint, headers)
        if json_request["next"] is None:
            return json_request["results"]
        else:
            return json_request["results"] + self.get_items(f"{endpoint.split('?')[0]}?{json_request['next'].split('?')[1]}", headers)

    def get_one_item(self, name: str, category: str) -> None:
        """
        The get_one_item function is used to get a single item from NetBox.
        The function takes two arguments: the name of the item and its category.
        The categories are as follows: region, site, location (or room), rack (or cabinet), device

        :param name: str: Specify the name of the item to be retrieved
        :param category: str: Determine what type of item you are looking for
        :return: None
        """
        if category.lower() == "region":
            region = self.get_items(f"api/dcim/regions?name={name}")[0]
            self.item_data = {region["name"]: region}
            self.item_tree = {region["name"]: {}}
            sites = self.get_items(f"api/dcim/sites?region_id={region['id']}&limit=0")
            locations = self.get_items(f"api/dcim/locations?region_id={region['id']}&limit=0")
            racks = self.get_items(f"api/dcim/racks?region_id={region['id']}&limit=0")
            devices = self.get_items(f"api/dcim/devices?region_id={region['id']}&limit=0")
            powerports = self.get_items(f"/api/dcim/power-ports?region_id={region['id']}&limit=0")
            for site in sites:
                self.insert_item_and_parents(site, self.find_key(region["name"]))
                self.item_data[site["name"]] = site
            for location in locations:
                self.insert_item_and_parents(location, self.find_key(location["site"]["name"]))
                self.item_data[location["name"]] = location
            for rack in racks:
                if "location" in rack and rack["location"] is not None:
                    self.insert_item_and_parents(rack, self.find_key(rack["location"]["name"]))
                else:
                    self.insert_item_and_parents(rack, self.find_key(rack["site"]["name"]))
                self.item_data[rack["name"]] = rack
            for device in devices:
                if "rack" in device and device["rack"] is not None:
                    self.insert_item_and_parents(device, self.find_key(device["rack"]["name"]))
                elif "location" in device and device["location"] is not None:
                    self.insert_item_and_parents(device, self.find_key(device["location"]["name"]))
                else:
                    self.insert_item_and_parents(device, self.find_key(device["site"]["name"]))
                self.item_data[device["name"]] = device
            for powerport in powerports:
                device = self.item_data[powerport["device"]["name"]]
                if "powerports" not in device:
                    device["powerports"] = []
                device["powerports"].append(powerport)
        elif category.lower() == "site":
            site = self.get_items(f"api/dcim/sites?name={name}")[0]
            self.item_data = {site["name"]: site}
            self.item_tree = {site["name"]: {}}
            locations = self.get_items(f"api/dcim/locations?region_id={region['id']}&limit=0")
            racks = self.get_items(f"api/dcim/racks?site_id={site['id']}&limit=0")
            devices = self.get_items(f"api/dcim/devices?site_id={site['id']}&limit=0")
            powerports = self.get_items(f"/api/dcim/power-ports?site_id={site['id']}&limit=0")
            for location in locations:
                self.insert_item_and_parents(location, self.item_tree[site["name"]])
                self.item_data[location["name"]] = location
            for rack in racks:
                if "location" in rack and rack["location"] is not None:
                    self.insert_item_and_parents(rack, self.find_key(rack["location"]["name"]))
                else:
                    self.insert_item_and_parents(rack, self.find_key(rack["site"]["name"]))
                self.item_data[rack["name"]] = rack
            for device in devices:
                if "rack" in device and device["rack"] is not None:
                    self.insert_item_and_parents(device, self.find_key(device["rack"]["name"]))
                elif "location" in device and device["location"] is not None:
                    self.insert_item_and_parents(device, self.find_key(device["location"]["name"]))
                else:
                    self.insert_item_and_parents(device, self.find_key(device["site"]["name"]))
                self.item_data[device["name"]] = device
            for powerport in powerports:
                device = self.item_data[powerport["device"]["name"]]
                if "powerports" not in device:
                    device["powerports"] = []
                device["powerports"].append(powerport)
        elif category.lower() == "location" or category.lower() == "room":
            location = self.get_items(f"api/dcim/locations?name={name}")[0]
            self.item_data = {location["name"]: location}
            self.item_tree = {location["name"]: {}}
            child_locations = self.get_items(f"api/dcim/locations?parent_id={location['id']}&limit=0")
            racks = self.get_items(f"api/dcim/racks?location_id={location['id']}&limit=0")
            devices = self.get_items(f"api/dcim/devices?location_id={location['id']}&limit=0")
            powerports = self.get_items(f"/api/dcim/power-ports?location_id={location['id']}&limit=0")
            for child_location in child_locations:
                self.insert_item_and_parents(child_location, self.item_tree)
                self.item_data[child_location["name"]] = child_location
                powerports += self.get_items(f"/api/dcim/power-ports?location_id={child_location['id']}&limit=0")
            for rack in racks:
                self.insert_item_and_parents(rack, self.find_key(rack["location"]["name"]))
                self.item_data[rack["name"]] = rack
            for device in devices:
                if "rack" in device and device["rack"] is not None:
                    self.insert_item_and_parents(device, self.find_key(device["rack"]["name"]))
                else:
                    self.insert_item_and_parents(device, self.find_key(device["location"]["name"]))
                self.item_data[device["name"]] = device
            for powerport in powerports:
                device = self.item_data[powerport["device"]["name"]]
                if "powerports" not in device:
                    device["powerports"] = []
                device["powerports"].append(powerport)
        elif category.lower() == "rack" or category.lower() == "cabinet":
            rack = self.get_items(f"api/dcim/racks?name={name}")[0]
            devices = self.get_items(f"api/dcim/devices?rack_id={rack['id']}&limit=0")
            self.item_data = {rack["name"]: rack}
            self.item_tree = {rack["name"]: {}}
            for device in devices:
                self.insert_item_and_parents(device, self.item_tree[device["rack"]["name"]])
                self.item_data[device["name"]] = device
            powerports = self.get_items(f"/api/dcim/power-ports?rack_id={rack['id']}&limit=0")
            for powerport in powerports:
                device = self.item_data[powerport["device"]["name"]]
                if "powerports" not in device:
                    device["powerports"] = []
                device["powerports"].append(powerport)
        else:
            item = self.get_items(f"api/dcim/devices?name={name}")[0]
            powerports = self.get_items(f"/api/dcim/power-ports?device_id={item['id']}&limit=0")
            for powerport in powerports:
                if "powerports" not in item:
                    item["powerports"] = []
                item["powerports"].append(powerport)
            self.item_tree = {item["name"]: {}}
            self.item_data = {item["name"]: item}

    def add_item(self, fields: dict[str, Any]) -> None:
        pass

    def modify_item(self, fields: dict[str, Any]) -> None:
        pass

    def models(self, model_class: str) -> dict:
        return {}

    def get_locations(self) -> list[str]:
        """
        The get_locations function returns a list of all the locations in the item_data dictionary.
        The function iterates through each item in the dictionary and checks if it has a site, location, and region key.
        If it hat the first key but does not have any of the next keys then that means that it is a location and should be added to our list.

        :return: A list of strings
        """
        return [
            self.item_data[item]["name"]
            for item in self.item_data
            if "site" in self.item_data[item] and "location" not in self.item_data[item] and "region" not in self.item_data[item]
        ]

    def get_racks(self, location: dict[str, Any]) -> list[dict[str, Any]]:
        """
        The get_racks function returns a list of rack names for the given location.

        :param location: dict[str, Any]: The location data
        :return: A list of rack names for the given location
        """
        return [
            self.item_data[item]["name"]
            for item in self.item_data
            if "location" in self.item_data[item]
            and self.item_data[item]["location"] is not None
            and "name" in self.item_data[item]["location"]
            and self.item_data[item]["location"]["name"] == location["name"]
            and "rack" not in self.item_data[item]
        ]


class DcTrackDataLoader(DataLoader):
    edcim = EDCIM.DCTRACK

    def order_dict(self, dictionary: dict) -> dict:
        """
        The order_dict function takes a dictionary as an argument and returns the same dictionary with its keys sorted alphabetically.
        If any of the values in the original dictionary are dictionaries themselves, then those sub-dictionaries will also be ordered.

        :param dictionary: Pass in the dictionary that is to be ordered
        :return: A dictionary with keys sorted in alphabetical order
        """
        return {k: self.order_dict(v) if isinstance(v, dict) else v for k, v in sorted(dictionary.items(), key=lambda x: str.lower(x[0]))}

    def get_all_items(self) -> None:
        """
        The get_all_items function is used to populate the item_tree and item_data dictionaries.
        The item_tree dictionary contains a nested dictionary of all items in the dcTrack database, organized by data center, room, rack and device.
        The item_data dictionary contains a flat list of all items fields in the dcTrack database.

        :return: None
        """
        self.item_tree = {self.edcim.name: {}}
        self.item_data = {}
        locations = self.post_data(
            "/api/v2/quicksearch/locations?pageSize=0",
            {},
        )["searchResults"]
        items = self.post_data(
            "/api/v2/quicksearch/items?pageSize=0",
            {},
        )[
            "searchResults"
        ]["items"]
        for location in locations:
            hierarchy = location["code"].split(" > ")
            level = self.item_tree[self.edcim.name]
            for step in hierarchy:
                if step not in level:
                    level[step] = {}
                level = level[step]
            self.item_data[step] = location

        for item in items:
            if "cmbCabinet" not in item:
                print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                continue
            if item["cmbCabinet"] not in self.item_tree[self.edcim.name][item["tiDataCenterCode"]][item["tiRoomNodeCode"]]:
                self.item_tree[self.edcim.name][item["tiDataCenterCode"]][item["tiRoomNodeCode"]][item["cmbCabinet"]] = {}
            if item["tiClass"] != "Cabinet":
                self.item_tree[self.edcim.name][item["tiDataCenterCode"]][item["tiRoomNodeCode"]][item["cmbCabinet"]][item["tiName"]] = {}
            self.item_data[item["tiName"]] = item

        self.item_data = dict(sorted(self.item_data.items(), key=lambda x: str.lower(x[0])))
        self.item_tree = self.order_dict(self.item_tree)

    def get_all_models(self) -> None:
        """
        The get_all_models function is used to populate the model_tree and model_data dictionaries.
        The model_tree dictionary contains all of the makes and models in a tree format, with makes as first floor and models as second.
        The model_data dictionary contains all of the data for each model.

        :return: None
        """
        data = self.post_data("/api/v2/quicksearch/models?pageSize=0", {})["searchResults"]["models"]
        for model in data:
            self.model_data[model["model"]] = model
            if model["make"] in self.model_tree:
                self.model_tree[model["make"]][model["model"]] = {}
            else:
                self.model_tree[model["make"]] = {model["model"]: {}}
        for make in self.model_tree:
            self.model_tree[make] = dict(sorted(self.model_tree[make].items(), key=lambda x: x[0].lower()))
        self.model_tree = dict(sorted(self.model_tree.items(), key=lambda x: x[0].lower()))

    def get_one_model(self, name: str) -> None:
        """
        The get_one_model function takes a model name as an argument and gets the model from the API if it exists
        
        :param name: str: Define the name of the model
        :return: None
        """
        search_payload = {
            "columns": [
                {"name": "model", "filter": {"eq": f'"{name}"'}},
            ],
        }
        model = self.post_data(
            "/api/v2/quicksearch/models?pageSize=0",
            search_payload,
        )["searchResults"][
            "models"
        ][0]

        self.model_tree = {model["make"]: {model["model"]: {}}}
        self.model_data = {model["model"]: model}

    def get_one_manufacturer(self, name: str) -> None:
        """
        The get_one_manufacturer function takes a manufacturer name as an argument and gets the manufacturer from the API if it exists, along with all its models
        
        :param name: str: Specify the name of the manufacturer
        :return: None
        """
        data = self.post_data(
            "/api/v2/quicksearch/models?pageSize=0",
            {
                "columns": [
                    {"name": "make", "filter": {"eq": f'"{name}"'}},
                ],
            },
        )[
            "searchResults"
        ]["models"]
        for model in data:
            self.model_data[model["model"]] = model
            if model["make"] in self.model_tree:
                self.model_tree[model["make"]][model["model"]] = {}
            else:
                self.model_tree[model["make"]] = {model["model"]: {}}
        for make in self.model_tree:
            self.model_tree[make] = dict(sorted(self.model_tree[make].items(), key=lambda x: x[0].lower()))
        self.model_tree = dict(sorted(self.model_tree.items(), key=lambda x: x[0].lower()))

    def get_one_item(self, name: str, category: str) -> None:
        """
        The get_one_item function is used to get the data for a single item.
        
        :param name: str: Define the name of the item you want to get
        :param category: str: Determine the type of item that is being searched for: room, datacenter, cabinet (everything else will not be used to search the item)
        :return: None
        """
        self.item_tree = {}
        self.item_data = {}
        if category.lower() == "room":
            locations = self.post_data(
                "/api/v2/quicksearch/locations?pageSize=0",
                {
                    "columns": [
                        {"name": "name", "filter": {"eq": f'"{name}"'}},
                        {"name": "hierarchyLevel", "filter": {"eq": "Room"}},
                    ]
                },
            )["searchResults"]
            items = self.post_data(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "tiRoomNodeCode", "filter": {"eq": f'"{name}"'}},
                    ]
                },
            )["searchResults"]["items"]
            for location in locations:
                self.item_tree[location["name"]] = {}
                self.item_data[location["name"]] = location

            for item in items:
                if "cmbCabinet" not in item:
                    print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                    continue
                if item["cmbCabinet"] not in self.item_tree[item["tiRoomNodeCode"]]:
                    self.item_tree[item["tiRoomNodeCode"]][item["cmbCabinet"]] = {}
                if item["tiClass"] != "Cabinet":
                    self.item_tree[item["tiRoomNodeCode"]][item["cmbCabinet"]][item["tiName"]] = {}
                self.item_data[item["tiName"]] = item
        elif category.lower().replace(" ", "") == "datacenter":
            locations = self.post_data(
                "/api/v2/quicksearch/locations?pageSize=0",
                {
                    "columns": [
                        {"name": "code", "filter": {"eq": f"{name}*"}},
                    ]
                },
            )["searchResults"]
            items = self.post_data(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "tiDataCenterCode", "filter": {"eq": f"{name}"}},
                    ]
                },
            )["searchResults"]["items"]
            for location in locations:
                hierarchy = location["code"].split(" > ")
                level = self.item_tree
                for step in hierarchy:
                    if step not in level:
                        level[step] = {}
                    level = level[step]
                self.item_data[location["name"]] = location

            for item in items:
                if "cmbCabinet" not in item:
                    print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                    continue
                if item["cmbCabinet"] not in self.item_tree[item["tiDataCenterCode"]][item["tiRoomNodeCode"]]:
                    self.item_tree[item["tiDataCenterCode"]][item["tiRoomNodeCode"]][item["cmbCabinet"]] = {}
                if item["tiClass"] != "Cabinet":
                    self.item_tree[item["tiDataCenterCode"]][item["tiRoomNodeCode"]][item["cmbCabinet"]][item["tiName"]] = {}
                self.item_data[item["tiName"]] = item
        elif category.lower() == "cabinet":
            items = self.post_data(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "cmbCabinet", "filter": {"eq": f'"{name}"'}},
                    ]
                },
            )[
                "searchResults"
            ]["items"]

            for item in items:
                if "cmbCabinet" not in item:
                    print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                    continue
                if item["cmbCabinet"] not in self.item_tree:
                    self.item_tree[item["cmbCabinet"]] = {}
                if item["tiClass"] != "Cabinet":
                    self.item_tree[item["cmbCabinet"]][item["tiName"]] = {}
                self.item_data[item["tiName"]] = item
        else:
            items = self.post_data(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "tiName", "filter": {"eq": f'"{name}"'}},
                    ]
                },
            )[
                "searchResults"
            ]["items"]

            for item in items:
                if "cmbCabinet" not in item:
                    print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                    continue
                if item["tiClass"] != "Cabinet":
                    self.item_tree[item["tiName"]] = {}
                self.item_data[item["tiName"]] = item

        self.item_data = dict(sorted(self.item_data.items(), key=lambda x: str.lower(x[0])))
        self.item_tree = self.order_dict(self.item_tree)

    def add_item(self, fields: dict) -> dict[str, Any]:
        """
        The add_item function adds an item to the dcTrack database.
        
        :param fields: dict: Pass the data to be added
        :return: A dict with the following keys: success(bool), message(str)
        """
        response = self.post_data("/api/v2/dcimoperations/items?returnDetails=true", fields)
        if "success" in response and not response["success"]:
            return {"success": False, "message": response["errorList"][0]}
        if "powerports" in fields:
            id = response["item"]["id"]
            powerports_dctrack = self.get_data(f"/api/v1/items/{id}/powerports")["powerports"]
            if len(powerports_dctrack) != len(fields["powerports"].values()):
                return {
                    "success": False,
                    "powerports": False,
                    "message": f"Item added without its powerports : wrong number of powerports, expected {len(powerports_dctrack)}, got {len(fields['powerports'].values())}",
                }

            for powerport in fields["powerports"].values():
                powerport["itemId"] = id
                response = self.put_data(f"/api/v1/items/{id}/powerports/{powerports_dctrack[0]['portId']}?proceedOnWarning=true", powerport)
                if "success" in response and not response["success"]:
                    return {
                        "success": False,
                        "powerports": False,
                        "message": f"Item added without all its powerports : {response['errorList'] if 'errorlist' in response else response['warningList']}",
                    }

                powerports_dctrack.pop(0)
        return {"success": True, "message": ""}

    def modify_item(self, fields: dict) -> dict[str, Any]:
        """
        The modify_item function takes a dictionary of fields as an argument.
        The function then searches for the item with the name specified in the tiName field, and if it finds one, modifies that item's attributes to match those specified in the fields dictionary.
        If no such item is found, it returns an error message saying so.
        
        :param fields: dict: Pass the fields of the item to be modified
        :return: A dict with the following keys: success(bool), message(str)
        """
        try:
            modified_item_id = self.post_data(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "tiName", "filter": {"eq": f'"{fields["tiName"]}"'}},
                    ]
                },
            )["searchResults"]["items"][0]["id"]
        except:
            return {"success": False, "message": f"No item found with name {fields['tiName']}. This should not be happening."}

        response = self.put_data(f"/api/v2/dcimoperations/items/{modified_item_id}?returnDetails=true", fields)
        if "success" in response and not response["success"]:
            return {"success": False, "message": response["errorList"][0]}
        if "powerports" in fields:
            id = response["item"]["id"]
            powerports_dctrack = self.get_data(f"/api/v1/items/{id}/powerports")["powerports"]
            if len(powerports_dctrack) != len(fields["powerports"].values()):
                return {
                    "success": False,
                    "powerports": False,
                    "message": f"Item added without its powerports : wrong number of powerports, expected {len(powerports_dctrack)}, got {len(fields['powerports'].values())}",
                }

            for powerport in fields["powerports"].values():
                powerport["itemId"] = id
                response = self.put_data(f"/api/v1/items/{id}/powerports/{powerports_dctrack[0]['portId']}?proceedOnWarning=true", powerport)
                if "success" in response and not response["success"]:
                    return {
                        "success": False,
                        "powerports": False,
                        "message": f"Item added without all its powerports : {response['errorList'] if 'errorlist' in response else response['warningList']}",
                    }

                powerports_dctrack.pop(0)
        return {"success": True, "message": ""}

    def models(self, model_class: str, invert: bool = False) -> dict[str, Any]:
        """
        The models function returns a dictionary of device models.
            The key is the make and the value is a list of dictionaries containing model names as keys and an empty list as values.
            If invert=True, then it will return all models that are not of class model_class.
        
        :param model_class: str: Specify the type of device you want to get models for
        :param invert: bool: Invert the result of the models function
        :return: A dictionary of models
        """
        device_models = {}
        for model in self.model_data.values():
            if model["class"] != model_class and not invert or model["class"] == model and invert:
                continue
            if model["make"] in device_models:
                device_models[model["make"]].append({model["model"]: []})
            else:
                device_models[model["make"]] = [{model["model"]: []}]
        for make in device_models:
            device_models[make].sort(key=lambda d: next(iter(d)).lower())
        return dict(sorted(device_models.items(), key=lambda x: x[0].lower()))

    def get_locations(self) -> list[str]:
        """
        The get_locations function returns a list of all the locations in the data.
            It does this by iterating through each item in self.item_data and checking if it has a hierarchyLevel key, which is only present for locations.
        
        :return: A list of strings
        """
        return [self.item_data[item]["name"] for item in self.item_data if "hierarchyLevel" in self.item_data[item]]

    def get_racks(self, location: dict[str, Any]) -> list[dict[str, Any]]:
        """
        The get_racks function returns a list of rack names for the given location.

        :param location: dict[str, Any]: The location data
        :return: A list of rack names for the given location
        """
        return [
            self.item_data[item]["tiName"]
            for item in self.item_data
            if "tiClass" in self.item_data[item]
            and self.item_data[item]["tiClass"] == "Cabinet"
            and self.item_data[item]["cmbLocation"] == location["code"]
        ]


class OGrEEDataLoader(DataLoader):
    edcim = EDCIM.OGREE

    def get_all_items(self) -> None:
        """
        The get_all_items function is used to get all items from the OGrEE server.
        It does this by first getting a tree of all items, and then getting the data for each item in that tree.
        
        :return: None
        """
        self.item_tree = {self.edcim.name: {}}
        self.item_data = {self.edcim.name: {}}
        tree: dict[str, Any] = self.get_data("/api/hierarchy?namespace=physical")["data"]["tree"]["physical"]
        tree.pop("*")
        data = self.get_data("/api/hierarchy/attributes")["data"]
        for item_id in tree:
            hierarchy = item_id.split(".")
            level = self.item_tree[self.edcim.name]

            for step in range(1, len(hierarchy) + 1):
                current_name = ".".join(hierarchy[0:step])
                if current_name not in level:
                    level[current_name] = {}
                level = level[current_name]
                self.item_data[current_name] = data[current_name]

    def get_all_models(self) -> None:
        pass

    def get_one_item(self, name: str, category: str) -> None:
        pass

    def get_one_model(self, name: str) -> None:
        pass

    def get_one_manufacturer(self, name: str) -> None:
        pass

    def add_item(self, fields: dict[str, Any]) -> dict[str, Any]:
        pass

    def modify_item(self, fields: dict[str, Any]) -> dict[str, Any]:
        pass

    def models(self, model_class: str, invert: bool = False) -> dict[str, Any]:
        pass

    def get_locations(self) -> dict[str, Any]:
        pass

    def get_racks(self, location: dict[str, Any]) -> dict[str, Any]:
        pass
