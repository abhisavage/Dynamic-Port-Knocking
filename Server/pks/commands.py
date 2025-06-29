import inspect
import logging
import threading
import time

from functools import wraps

from .permissions import Permissions
from .channels import Channels
from .config import Config
from .utils import Utils
from .core import Core


def permissions_required(*perms):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            obj = args[0]
            if obj.permissions.is_user_allowed(str(obj.user_id), list(perms)):
                result = function(*args, *kwargs)
            else:
                result = "Action forbidden ; insufficient rights."
                logging.info(result + f" User id: {obj.user_id} ; Function called: {function.__name__}")
            return result
        return wrapper
    return decorator


class Commands:
    def __init__(self, chan: Channels):
        self.running = False
        self.permissions = Permissions()
        self.user_id = "1"
        self.permissions.set_telegram_admins()
        self.channels = chan
        self._sequence_thread = None  # Thread for periodic sequence generation
        self._sequence_thread_stop_event = threading.Event()
        self._sequence_thread_user_ids = []  # Track ALL users who requested /generate
        self.start()

    def __del__(self):
        self.user_id = "1"
        self.stop()

    @permissions_required("none")
    def invalid(self) -> None:
        
        return

    @permissions_required("none")
    def help(self, whitelisted_functions: list) -> str:
        
        if self.running:
            string = "Commands available: \n\n"
            for func in inspect.getmembers(Commands, predicate=inspect.isfunction):  # func is a 2-tuple.
                function_name = func[0]
                if "/" + function_name in whitelisted_functions:
                    string += "/{}: {}\n".format(function_name, inspect.getdoc(getattr(Commands, function_name)))
            return string

    @permissions_required("manage_sequences")
    def target_port(self) -> str:
        return str(Config.target_port)

    @permissions_required("modify_bot_behaviour", "admin_access")
    def add_perm(self, user: str, group: str) -> str:
        
        if not self.permissions.is_group_valid(group):
            return f"Group {group} is invalid !"
        self.permissions.add_user_to_group(user, group)
        return f"User {user} successfully added to group {group} !"

    @permissions_required("modify_bot_behaviour", "admin_access")
    def remove_perm(self, user: str, group: str) -> str:
        
        if not self.permissions.is_group_valid(group):
            return f"Group {group} is invalid !"
        self.permissions.remove_user_from_group(user, group)
        return f"User {user} successfully removed from group {group} !"

    @permissions_required("manage_sequences")
    def generate(self) -> str:
        # If already running, add this user to the list
        if self._sequence_thread and self._sequence_thread.is_alive():
            if self.user_id not in self._sequence_thread_user_ids:
                self._sequence_thread_user_ids.append(self.user_id)
                return f"Added you to the sequence generation list. Total users: {len(self._sequence_thread_user_ids)}"
            else:
                return "You are already receiving periodic sequences. Use /stop to stop for everyone."

        # Start periodic sequence generation in a background thread
        self._sequence_thread_stop_event.clear()
        self._sequence_thread_user_ids = [self.user_id]  # Start with this user
        self._sequence_thread = threading.Thread(target=self._periodic_sequence_update, daemon=True)
        self._sequence_thread.start()

        # Also generate and send the first sequence immediately
        if Config.use_open_sequence:
            seq = Config.open_sequence
        else:
            seq = Core.generate_new_sequence()
        Core.set_open_sequence(seq)
        message = "New sequence: " + ", ".join([str(p) for p in seq])
        if not self.running:
            message += "\nWARNING: the bot is stopped. Start it with /start."
        # Send to the requesting user only
        self.channels.bot.send_message(self.user_id, message)
        return "Started periodic port sequence generation. Use /stop to stop for everyone."

    def _periodic_sequence_update(self):
        while not self._sequence_thread_stop_event.is_set():
            time.sleep(60)
            if self._sequence_thread_stop_event.is_set():
                break
            if Config.use_open_sequence:
                seq = Config.open_sequence
            else:
                seq = Core.generate_new_sequence()
            Core.set_open_sequence(seq)
            message = "New sequence: " + ", ".join([str(p) for p in seq])
            if not self.running:
                message += "\nWARNING: the bot is stopped. Start it with /start."
            # Send to ALL users who requested /generate
            for user_id in self._sequence_thread_user_ids:
                self.channels.bot.send_message(user_id, message)

    @permissions_required("admin_access")
    def status(self) -> str:
        
        return "Running" if self.running else "Stopped"

    @permissions_required("admin_access")
    def print_config(self, attr: str or None) -> str:
        
        attributes = [d for d in dir(Config) if not d.startswith("__")]
        config = "Value:\n"

        if attr == "help":
            return "Available attributes: all, " + ", ".join(attributes)

        if attr not in attributes:  # If the attribute does not exist
            return "This attribute does not exist. Use \"/print_config help\" or \"/help\" for more information."

        if attr == "all":
            for a in attributes:
                config += getattr(Config, a)  # Get attribute value

        config += getattr(Config, attr)

        return str(config)

    @permissions_required("admin_access")
    def print_broadcast_list(self) -> str:
        
        return ", ".join(self.channels.list_active_channels())

    @permissions_required("modify_bot_behaviour")
    def forget(self, chat_id: str) -> None:
        
        self.channels.disable(chat_id)

    @permissions_required("modify_bot_behaviour")
    def list_groups_members(self) -> str:
        
        message = ""
        for group in self.permissions.get_valid_groups():
            message += group + ": " + ", ".join(self.permissions.get_group_members(group)) + "\n"
        return message

    @permissions_required("modify_bot_behaviour")
    def start(self) -> str:
        
        if not self.running:
            if not Utils.start_service("knockd"):
                return "Could not start knockd ; unknown error."
            self.running = True
            return "Started knockd."
        else:
            return "Knockd already running."

    @permissions_required("modify_bot_behaviour")
    def stop(self) -> str:
        # Stop periodic sequence generation if running
        if self._sequence_thread and self._sequence_thread.is_alive():
            self._sequence_thread_stop_event.set()
            self._sequence_thread.join(timeout=2)
            self._sequence_thread = None
            self._sequence_thread_user_ids = []  # Clear all users
        # Stop knockd as before
        if self.running:
            if not Utils.stop_service("knockd"):
                return "Could not stop knockd ; unknown error."
            self.running = False
            return "Stopped knockd and periodic sequence generation."
        else:
            return "Knockd already stopped. Periodic sequence generation (if any) also stopped."

    @permissions_required("modify_bot_behaviour", "admin_access")
    def shutdown(self):
        
        self.stop()
        raise SystemExit
