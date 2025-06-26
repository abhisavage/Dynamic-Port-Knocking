import logging
import time

from .telegram import TelegramBot
from .channels import Channels
from .commands import Commands
from .config import Config


logging.basicConfig(
    format='%(asctime)s - %(message)s',
    level=logging.INFO,
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename="/var/log/pks.log",
    filemode="a+",
)


class PKS:

    """
    Main class

    .. seealso :: run_server.py
    """

    def __init__(self, bot: TelegramBot):
        self.bot = bot
        self.chan = Channels(bot)
        self.commands_o = Commands(self.chan)

    def __del__(self):
        del self.commands_o
        del self.chan

    def __set_commands(self, update: dict) -> None:
        
        self.commands_l = {
            "/generate":
                (self.commands_o.generate, 0, []),
            "/start":
                (self.commands_o.start, 0, []),
            "/stop":
                (self.commands_o.stop, 0, []),
            "/forget":
                (self.commands_o.forget, 0, [update['message']['chat']['id']]),
            "/shutdown":
                (self.commands_o.shutdown, 0, []),
            "/list_groups_members":
                (self.commands_o.list_groups_members, 0, []),
            "/add_perm":
                (self.commands_o.add_perm, 2, []),
            "/remove_perm":
                (self.commands_o.remove_perm, 2, []),
        }
        # Adds the "/help" command.
        # Help will only print documentation for the functions listed above (in commands_l).
        self.commands_l.update({"/help": [self.commands_o.help, 0, [list(self.commands_l.keys())]]})

    def get_chat_text(self, update: dict) -> str:
        
        try:
            chat_text = update['message']['text']  # May raise KeyError for some messages.
        except KeyError:
            chat_text = None
        return chat_text

    def get_chat_id(self, update: dict) -> str:
        
        return update['message']['chat']['id']

    def get_message_id(self, update: dict) -> str:
       
        return update['message']['message_id']

    def get_user_id(self, update: dict) -> str:
        
        return update['message']['from']['id']

    def are_args_valid(self, found_args, expected_args) -> tuple:
        if found_args > expected_args:
            message = f"Too many arguments: expected {expected_args}, got {found_args}. Please refer to \"/help\"."
            return False, message
        elif found_args < expected_args:
            message = f"Too few arguments: expected {expected_args}, got {found_args}. Please refer to \"/help\"."
            return False, message
        return True, None

    def process(self, update: dict) -> None:
        self.__set_commands(update)

        chat_text: str = self.get_chat_text(update)
        chat_id: str = self.get_chat_id(update)
        message_id: str = self.get_message_id(update)
        user_id: str = self.get_user_id(update)

        # Register the channel by adding it to the broadcast list.
        self.chan.add(chat_id)

        # Set the "user_id" attribute of object "commands_o".
        # It will be used to check if the user is allowed to launch the command.
        self.commands_o.user_id = user_id

        chat_msg = chat_text.split(" ")

        command = chat_msg[0].split("@")[0]
        func = self.commands_l.get(command, [self.commands_o.invalid])[0]
        num_exp_args = self.commands_l.get(command, [None, 0])[1]
        
        args = self.commands_l.get(command, [None, None, []])[2]

        chat_msg.pop(0)  # Removes the command, to only have the arguments.
        original_args_length = len(args)

        for arg in chat_msg:
            args.append(arg)

        found_args = len(args) - original_args_length

        valid, message = self.are_args_valid(found_args, num_exp_args)
        if valid:
            # Call the function with its arguments and store the returned value.
            # This value can either be a string (str) or nothing (None).
            message = (func)(*args)

        if message:
            self.bot.send_message(chat_id, message, message_id)

    def main(self, offset: int = 0) -> None:
        
        while True:
            all_updates = self.bot.get_updates(offset)

            if len(all_updates) > 0:
                for current_update in all_updates:
                    try:
                        # Filters the updates: only process the ones who starts with "/".
                        try:
                            upd_txt = current_update['message']['text']  # May raise KeyError for some messages.
                        except KeyError:
                            pass
                        else:
                            upd_time = current_update['message']['date']
                            if upd_txt.startswith("/") and (int(time.time()) - upd_time) < Config.telegram_timeout:
                                logging.debug(current_update)
                                self.process(current_update)
                    except SystemExit:
                        del self
                        raise SystemExit

                    update_id = current_update['update_id']
                    offset = update_id + 1
