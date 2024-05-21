from dataclasses import dataclass
import traceback
import toml


class ConfigHandler:

    @dataclass
    class SDCIM:
        url: str
        token: str
        default_items: str
        default_models: str

    dcims: dict[str, SDCIM] = {}
    headers: dict

    class DCIMNotLoaded(Exception):
        wrongDCIMS: list[str]

        def __init__(self, wrongDCIMS: list[str], *args) -> None:
            """
            The __init__ function is called when the class is instantiated.
            It takes in a list of strings, which are DCIMs that were not found in the database, and passes them to its parent class.
            :param wrongDCIMS: list[str]: Store the list of dcims that are not in the correct format
            :param *args: Pass any number of arguments to the parent class
            :return: None
            """
            self.wrongDCIMS = wrongDCIMS
            super().__init__(*args)

    def LoadConfig(self, configPath: str) -> None:
        """
        The LoadConfig function loads the configuration file and sets up the headers for requests.
        It also creates a dictionary of SDCIM objects, which are used to store information about each DCIM.
        The function raises an exception if there is a problem with loading any of the DCIMs.

        :param configPath: str: Specify the path to the configuration file
        :return: None
        """
        try:
            config = toml.load(configPath)
            self.headers = config["headers"]
        except:
            raise Exception("wrong path")
        wrongDCIMS = []
        for dcim in config["DCIM"]:
            try:
                self.dcims[dcim] = self.SDCIM(**config["DCIM"][dcim])
            except:
                traceback.print_exc()
                wrongDCIMS.append(dcim)
        if len(wrongDCIMS) > 0:
            raise self.DCIMNotLoaded(wrongDCIMS)
