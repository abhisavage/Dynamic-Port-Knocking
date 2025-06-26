class Config:
    telegram_token: str = "8077714410:AAH2b_asxlWgo5kMH3KxC10uPRlLGOeWhak"
    telegram_timeout: int = 5

    telegram_user_admin_list: list = ["5145713074"]
    telegram_user_whitelist: list = ["5145713074"]
    telegram_user_blacklist: list = []
    acceptable_port_range: range = range(1025, 65536)
    ports_blacklist: list = []
    target_port: int = 22
    use_open_sequence: bool = False
    open_sequence: list = [100, 200, 300]
    sequences_length: int = 3
    knockd_config_file: str = "/etc/knockd.conf"
    packet_manager: str = "apt"
    network_interface: str = "eth0"
