#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
    This is a main program in Aria helper CHRLINE Version.
    Versoin: CHR_Aria 1.3.0
    Type: single (useThrift)
    Auther: YiJhu (https://github.com/yijhu/)
    Web: (https://profile.yijhu.xyz)
    License: BSD 3-Clause License
    Repository: (https://github.com/YiJhu/Aria_helper)
    ------------------------------------------------------
    Library: CHRLINE (ver: 2.5.24)
'''
from CHRLINE import *
import re
import json
import time
import timeit
import codecs
import datetime
import threading
import concurrent


bot = CHRLINE(
    authTokenOrEmail="",
    password=None,
    os_name="Aria_helper"
    device="DESKTOPWIN",
    useThrift=True
)

bot_name = ""

try:
    bot.getE2EESelfKeyData()
except:
    bot.registerE2EESelfKey()


dbOpen = codecs.open("./data/auther.json", "r", "utf-8")
db = json.load(dbOpen)
dbOpen.close()

Admin = []  # Admin
for admin in db['admin']:
    Admin.append(admin)

Owner = []  # Owner
for owner in db['owner']:
    Owner.append(owner)

# rev = 0
rev = bot.getLastOpRevision()

helplist = "/help\n/speed\n/time\n/me\n/mid:{get your or someone by Tag}\n/userinfo:{Mids or Tags}\n/gid"


def nameUpdate():  # update bot name
    while True:
        try:
            try:
                bot.updateProfileAttribute(
                    2, f"{(bot_name).split()[0]} {datetime.datetime.now().strftime('(%H:%M)')}")
                bot.log("nameUpdate")
            except Exception as e:
                bot.log(f"Name Update Error: {e.message}")
            time.sleep(300)
        except:
            return


thread = threading.Thread(target=nameUpdate, daemon=True).start()

while True:
    Ops = bot.fetchOps(rev)
    for op in Ops:
        if op.type != 0:
            rev = max(rev, op.revision)
            # print('%s\n\n' % (op))
            if op.type == 26:  # for receive message
                try:
                    msg = op.message
                    text = msg.text
                    if msg.contentType == 0:  # for text
                        if msg.toType == 2:  # for chatrooms
                            # E2EE Support
                            if msg.contentMetadata is not None and 'e2eeVersion' in msg.contentMetadata:
                                text = bot.decryptE2EETextMessage(msg)

                            if msg._from in Owner or msg._from in Admin:
                                if text in "/help":
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        help = str(helplist)
                                        if msg._from in Owner:
                                            pass
                                            # help += str(
                                            #     "\n/exec:{text}\n/rename:{text}\n/rebio:{text}\n/repic:{path}\n/Kickall\n/oplist\n/addop:{Tags}\n/delop:{Tags}")
                                        else:
                                            continue
                                        executor.submit(bot.replyMessage(
                                            msg, f"【HELP COMMAND】\n{help}"))
                                    bot.replyMessage(
                                        msg, "[Author Page]\nhttps://profile.yijhu.xyz/\n[Open source]\nhttps://github.com/YiJhu/Aria_helper/\n[Privacy Policy]\nhttps://yijhu.xyz/privacy/\n[Support this project]\nhttps://ko-fi.com/archibald_tw")

                                if text in '/speed':  # speed test
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        speed = timeit.timeit(
                                            '"-".join(str(n) for n in range(100))', number=10000)
                                        executor.submit(bot.replyMessage(
                                            msg, f"SpeedTest： {speed} s"))

                                if text in '/time':  # get time
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        stime = bot.getServerTime()
                                        executor.submit(bot.replyMessage(msg,  "【Now Time】\n" + time.strftime(
                                            '%Y-%m-%d %I:%M:%S %p', time.localtime(stime/1000))))

                                if text in '/me':  # get your contact
                                    try:
                                        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                            executor.submit(bot.sendContact(
                                                msg.to, msg._from, "yijhu.xyz"))
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'{e.message}')

                                # get (your or someone) LINE-legy mid
                                if text.startswith('/mid'):
                                    try:
                                        mentionees = bot.getMentioneesByMsgData(
                                            msg)
                                        if not mentionees:
                                            bot.replyMessage(msg, msg._from)
                                        else:
                                            mentions = []
                                            reply = ''
                                            sent_mids = []  # a list to store sent mid
                                            for mid in mentionees:
                                                if mid in sent_mids:  # skip if the mid has already been sent
                                                    continue
                                                _reply = f"@{bot.getContact(mid).displayName}"
                                                mentions.append({
                                                    'S': len(reply) if reply == '' else len(reply) + 1,
                                                    'L': len(_reply),
                                                    'M': mid
                                                })
                                                _reply += f' {mid}'
                                                reply += _reply if reply == '' else f"\n{_reply}"
                                                # add the mid to the list
                                                sent_mids.append(mid)
                                            bot.replyMessage(
                                                msg, reply, contentMetadata=bot.genMentionData(mentions))
                                    except Exception as e:
                                        bot.replyMessage(msg, f"{e}")

                                # get user infomation via mentions or mids
                                if text.startswith("/userinfo:"):
                                    user_mids = bot.getMentioneesByMsgData(msg) or re.findall(
                                        re.compile(r'(?<![a-f0-9])u[a-f0-9]{32}(?![a-f0-9])'), text[10:])
                                    for user_mid in set(user_mids):
                                        try:
                                            user = bot.getContact(user_mid)
                                            user_info = (
                                                f"User Name:\n{user.displayName}\n"
                                                f"User Mid:\n{user.mid}\n"
                                                f"Status Message:\n(Only show 100 words!)\n{user.statusMessage[:100]}\n"
                                                f"Profile Link:\n{bot.LINE_PROFILE_CDN_DOMAIN}/{user.pictureStatus}"
                                            )
                                            bot.replyMessage(msg, user_info)
                                        except Exception as e:
                                            bot.replyMessage(
                                                msg, f'【MID ERROR】\n{e.message}')

                                if text in '/gid':  # get chat room id
                                    bot.replyMessage(msg, msg.to)


# finish it by yourself, if you want to add more command, you can add it here.
# or you can donate me to get more command and function.
# 你可以自己加入更多指令，或者贊助我來獲得更多指令和功能，去吧、孩子。

                except:
                    pass
