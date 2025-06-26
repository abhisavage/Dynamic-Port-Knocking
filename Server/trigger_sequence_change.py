import pks

if not pks.Config.use_open_sequence:
    bot = pks.BotHandler()

    chan = pks.Channels(bot)
    cmd = pks.Commands(chan)

    message = "New SSH connection registered.\n"
    message += cmd.generate()

    if type(message) == str:
        chan.broadcast(message)

    del bot
