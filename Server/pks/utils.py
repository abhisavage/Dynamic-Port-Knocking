# -*- coding: UTF8 -*-

import subprocess
import logging

from .config import Config


class Utils:


    @staticmethod
    def start_service(service: str) -> bool:
        
        code = int(subprocess.call("sudo systemctl start " + service, shell=True))
        if code == 0:
            logging.info("Started service %s successfully (code %s).", service, code)
            return True
        else:
            logging.error("Tried to start service %s but returned code %s.", service, code)
            return False

    @staticmethod
    def stop_service(service: str) -> bool:
        
        code = int(subprocess.call("sudo systemctl stop " + service, shell=True))
        if code == 0:
            logging.info("Stopped service %s successfully (code %s).", service, code)
            return True
        else:
            logging.error("Tried to stop service %s but returned code %s.", service, code)
            return False

    @staticmethod
    def restart_service(service: str) -> bool:
        
        if Utils.stop_service(service) and Utils.start_service(service):
            return True
        else:
            return False

    @staticmethod
    def create_log_file(path: str = "/var/log/pks.log") -> None:
        open(path, 'w').close()

    @staticmethod
    def install_package(packet_manager: str, package: str) -> bool:
        
        code = int(subprocess.call("sudo {} install {} -y".format(packet_manager, package), shell=True))
        if code == 0:
            return True
        else:
            return False

    @staticmethod
    def filter_port_list(port_list: list) -> list:
        
        first_acceptable_port: int = Config.acceptable_port_range[0]
        last_acceptable_port: int = Config.acceptable_port_range[-1:][0]

        for i, port in enumerate(port_list):
            while port in Config.ports_blacklist or port not in Config.acceptable_port_range:
                port += 1
                if port > last_acceptable_port:
                    port = (port % last_acceptable_port) + first_acceptable_port
                port_list[i] = port
        return port_list
