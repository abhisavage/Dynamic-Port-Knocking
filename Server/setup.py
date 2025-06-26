import sys

from pks.config import Config
from pks.utils import Utils
from pks.core import Core


if not sys.platform.startswith("linux"):
    input("This server can only run on Linux distributions. Press enter to quit...")
    exit()


def main():
    Utils.install_package(
        Config.packet_manager,
        "knockd"
    )
    Core.configure_knockd([100, 200, 300])
    Utils.create_log_file()
    Utils.start_service("knockd")


if __name__ == "__main__":
    main()
