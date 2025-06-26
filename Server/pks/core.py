import logging

from hashlib import sha256
from random import randint

from .config import Config
from .utils import Utils


class Core:


    @staticmethod
    def generate_new_sequence(num: int = Config.sequences_length, seed: int or None = None) -> list:
        logging.debug("Creating a new sequence with args num: int = %s, seed: int = %s.", Config.sequences_length, seed)

        first_acceptable_port: int = Config.acceptable_port_range[0]
        last_acceptable_port: int = Config.acceptable_port_range[-1:][0]

        logging.debug("First acceptable port: %d ; last acceptable port: %d",
                      first_acceptable_port, last_acceptable_port)

        if seed:
            port_list = [
                int(
                    # Hashes the index and the seed.
                    sha256(
                        str(i + seed).encode("utf-8")
                    ).hexdigest(),
                    16  # Converts the hexadecimal digest to decimal.
                ) for i, _ in enumerate(range(num))
            ]
        else:
            port_list = [
                randint(
                    # Applies the range to the randint function
                    first_acceptable_port,
                    last_acceptable_port
                ) for _ in range(num)
            ]

        port_list = Utils.filter_port_list(port_list)

        return port_list

    @staticmethod
    def set_open_sequence(port_sequence: list) -> None:
        Core.configure_knockd(port_sequence)
        Utils.restart_service("knockd")

    @staticmethod
    def configure_knockd(seq: list) -> None:

        def knockd_conf(new_sequence: list) -> str:
            
            return """
[options]
    logfile     = /var/log/knockd.log
    interface   = any

[opencloseSSH]
    sequence                = {open_sequence}
    seq_timeout             = 60
    start_command           = /sbin/iptables -I INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
    tcpflags                = syn
    cmd_timeout             = 60
    stop_command            = /sbin/iptables -D INPUT -s %IP% -p tcp --dport {ssh_port} -j ACCEPT
        """.format(
                open_sequence=", ".join([str(p) for p in new_sequence]),
                network_interface=Config.network_interface,
                ssh_port=Config.target_port,
            )
        # End of function knockd_conf()

        with open(Config.knockd_config_file, "w") as conf_file:
            conf_file.write(knockd_conf(seq))
