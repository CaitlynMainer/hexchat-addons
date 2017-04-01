__module_name__ = "Bridge Bot integration"
__module_version__ = "1.5"
__module_description__ = "Integrates messages from IRC Bridge Bots"

import hexchat, re
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))

				   

ignorelist = {}
botlist = {}

def loadlist():
    global ignorelist
    global botlist
    try:
        ignorelist = eval(hexchat.get_pluginpref('ignorelist'))
        botlist = eval(hexchat.get_pluginpref('botlist'))
    except Exception as e:
        hexchat.prnt(str(e))

def savelist():
    global ignorelist
    global botlist
    ignorelist = list(filter(None, ignorelist))
    hexchat.set_pluginpref('ignorelist', str(ignorelist))
    hexchat.set_pluginpref('botlist', str(botlist))
    loadlist()
    printlist()

def nested(x, ys):
    return any(x in nested for nested in ys)
	
def privmsg(word, word_eol, userdata, attrs):
    global ignorelist
    global botlist
    def send(*args, **kwargs):
        if attrs.time:
            kwargs.setdefault("time", attrs.time)
        return hexchat.emit_print(*args, **kwargs)

    bprefix = word[0]
    if bprefix[0:1] != ':':
        return hexchat.EAT_NONE

    bprefix = bprefix[1:]
    bnick, _, bhost = split_prefix(bprefix)
    for key in botlist:
        if bnick.lower() == key.lower():
            channel = word[2]
            nick = word[3][1:]
            for iggynick in ignorelist:
                if re.search(iggynick.lower(), nick.lower().replace('\u200b', '')) is not None:
                    return hexchat.EAT_ALL
            if nick == '*':
                if check_highlight(word_eol[5] if len(word_eol) >= 6 else ""):
                    send("Channel Action Hilight", botlist[key] + hexchat.strip(word[4]), word_eol[5] if len(word_eol) >= 6 else "")
                    hexchat.command('gui color 3')
                else:
                    send("Channel Action", botlist[key] + hexchat.strip(word[4]), word_eol[5] if len(word_eol) >= 6 else "")
                    hexchat.command('gui color 2')
            elif nick[0] == '<':
                found = False
                if nick[-1] == '>':
                    found = True
                else:
                    while len(word) > 4:
                        nick += " " + hexchat.strip(word[4])
                        del word[4]
                        del word_eol[4]
                        if nick[-1] == '>':
                            found = True
                            break
                if not found:
                    return hexchat.EAT_NONE
                if check_highlight(word_eol[4] if len(word_eol) >= 5 else ""):
                    send("Channel Msg Hilight", botlist[key] + hexchat.strip(nick)[1:-1], word_eol[4] if len(word_eol) >= 5 else "")
                    hexchat.command('gui color 3')
                else:
                    send("Channel Message", botlist[key] + hexchat.strip(nick)[1:-1], word_eol[4] if len(word_eol) >= 5 else "")
                    hexchat.command('gui color 2')
            elif nick[0] == '(':
                found = False
                if nick[-1] == ')':
                    found = True
                else:
                    while len(word) > 4:
                        nick += " " + hexchat.strip(word[4])
                        del word[4]
                        del word_eol[4]
                        if nick[-1] == ')':
                            found = True
                            break
                if not found:
                    return hexchat.EAT_NONE
                if check_highlight(word_eol[4] if len(word_eol) >= 5 else ""):
                    send("Channel Msg Hilight", botlist[key] + hexchat.strip(nick)[1:-1], word_eol[4] if len(word_eol) >= 5 else "")
                    hexchat.command('gui color 3')
                else:
                    send("Channel Message", botlist[key] + hexchat.strip(nick)[1:-1], word_eol[4] if len(word_eol) >= 5 else "")
                    hexchat.command('gui color 2')
            else:
                return hexchat.EAT_NONE
            return hexchat.EAT_HEXCHAT

    return hexchat.EAT_NONE

def check_highlight(message):
    hilights = hexchat.get_prefs("irc_extra_hilight")
    hilight_list = hilights.split(",")
    if hexchat.get_info("nick") in message:
        return True
    elif any(message.find(check) > -1 for check in hilight_list):
        return True
    else:
        return False
	
def split_prefix(prefix):
    if '!' in prefix:
        nick, _, userhostpart = prefix.partition('!')
        user, _, host = userhostpart.partition('@')
    else:
        nick, _, host = prefix.partition('@')
        user = ''
    return (nick, user, host)
    
def addignore(word, word_eol, userdata):
    global ignorelist
    ignorelist.append(word[1])
    hexchat.prnt("Added " + word[1] + " to your ignore list.")
    savelist()
    return hexchat.EAT_ALL
    
def addbot(word, word_eol, userdata):
    global botlist
    if len(word) != 3:
        hexchat.prnt("Syntax is /addbot botnick prefix: /addbot Corded ^")
        return hexchat.EAT_ALL
    botlist.update({word[1]:word[2]})
    hexchat.prnt("Added " + word[1] + " to your bot list with prefix " + word[2] + ".")
    savelist()
    return hexchat.EAT_ALL
    
def delbot(word, word_eol, userdata):
    global botlist
    try:
        botlist.pop(word[1], None)
        hexchat.prnt("Removed " + word[1] + " from your bot list.")
        savelist()
    except: pass
    return hexchat.EAT_ALL

def delignore(word, word_eol, userdata):
    global ignorelist
    try:
        ignorelist.remove(word[1])
        hexchat.prnt("Removed " + word[1] + " from your ignore list.")
        savelist()
    except: pass
    return hexchat.EAT_ALL

def disignore(word, word_eol, userdata):
    printlist()
    return hexchat.EAT_ALL
    
def printlist():
    global ignorelist
    global botlist
    if len(ignorelist) == 0:
        hexchat.prnt('Ignorelist is empty')
    else:
        hexchat.prnt('Ignorelist: ' + ', '.join(ignorelist))
    if len(botlist) == 0:
        hexchat.prnt('Botlist is empty')
    else:
        hexchat.prnt('Bot List: ' + ', '.join("{!s}={!r}".format(key,val) for (key,val) in botlist.items()))

loadlist()
hexchat.hook_command("addignore", addignore)
hexchat.hook_command("delignore", delignore)
hexchat.hook_command("ignorelist", disignore)
hexchat.hook_command("addbot", addbot)
hexchat.hook_command("delbot", delbot)
hexchat.hook_server_attrs('PRIVMSG', privmsg)

hexchat.prnt(__module_name__ + " " + __module_version__ + " loaded!")
printlist()