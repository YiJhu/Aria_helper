#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
    This is a main program in Aria helper CHRLINE Version.
    Versoin: CHR_Aria 1.3.0
    Type: single
    Auther: YiJhu (https://github.com/yijhu/)
    Web: (https://profile.yijhu.xyz)
    License: BSD 3-Clause License
    Repository: (https://github.com/YiJhu/Aria_helper)
    ------------------------------------------------------
    Library: CHRLINE (ver: 2.5.24)
'''
from CHRLINE import CHRLINE
import re
import json
import time
import timeit
import codecs
import datetime
import threading
import concurrent


bot = CHRLINE(authTokenOrEmail="", password=None,
              device="DESKTOPWIN", os_name="Aria helper", useThrift=False)

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

helplist = "/help\n/speed\n/time\n/me\n/mid:{get your or someone by Tag}\n/userinfo:{Mids or Tags}\n/gid\n/getcontact:{Mids or Tags}\n/ginfo\n/gowner\n/url:{on/off}\n/regname:{new group name}\n/bye\n/kick:{mid}\n/mk:@{Tags}\n/cancel\n/data:{num}"

def nameUpdate(): # update bot name
    while True:
        try:
            try:
                bot.updateProfileAttribute(
                    2, f"{(bot_name).split()[0]} {datetime.datetime.now().strftime('(%H:%M)')}")
                bot.log("nameUpdate")
            except Exception as e:
                bot.log(f"nameUpdate Error: {e}")
            time.sleep(300)
        except:
            return


thread = threading.Thread(target=nameUpdate, daemon=True).start()

while True:
    Ops = bot.fetchOps(rev)
    for op in Ops:
        if op and 0 not in op and op[3] != 0:
            rev = max(rev, op[1])
            # print('%s\n\n' % (op))
            if op[3] == 26:  # for receive message
                try:
                    msg = op[20]
                    if msg[15] == 0:  # for text
                        if msg[3] == 2:  # for chatrooms
                            # E2EE Support
                            if 18 in msg and msg[18] is not None and 'e2eeVersion' in msg[18]:
                                msg[10] = bot.decryptE2EETextMessage(msg)

                            if msg[1] in Owner or msg[1] in Admin:
                                if msg[10] in '/help':  # help commands
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        help = str(helplist)
                                        if msg[1] in Owner:
                                            help += str(
                                                "\n/exec:{text}\n/rename:{text}\n/rebio:{text}\n/repic:{path}\n/Kickall\n/oplist\n/addop:{Tags}\n/delop:{Tags}")
                                        else:
                                            continue
                                        executor.submit(bot.replyMessage(
                                            msg, f"【HELP COMMAND】\n{help}"))
                                    bot.replyMessage(
                                        msg, "[Author Page]\nhttps://profile.yijhu.xyz/\n[Open source]\nhttps://github.com/YiJhu/Aria_helper/\n[Privacy Policy]\nhttps://yijhu.xyz/privacy/\n[Support this project]\nhttps://ko-fi.com/archibald_tw")

                                if msg[10] in '/speed':  # speed test
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        speed = timeit.timeit(
                                            '"-".join(str(n) for n in range(100))', number=10000)
                                        executor.submit(bot.replyMessage(
                                            msg, f"SpeedTest： {speed} s"))

                                if msg[10] in '/time':  # get time
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                        stime = bot.getServerTime()
                                        executor.submit(bot.replyMessage(msg,  "【Now Time】\n" + time.strftime(
                                            '%Y-%m-%d %I:%M:%S %p', time.localtime(stime/1000))))

                                if msg[10] in '/me':  # get your contact
                                    try:
                                        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                            executor.submit(bot.sendContact(
                                                msg[2], msg[1], "yijhu.xyz"))
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'{e.message}')

                                # get (your or someone) LINE-legy mid
                                if msg[10].startswith('/mid'):
                                    try:
                                        mentionees = bot.getMentioneesByMsgData(
                                            msg)
                                        if not mentionees:
                                            bot.replyMessage(msg, msg[1])
                                        else:
                                            mentions = []
                                            reply = ''
                                            sent_mids = []  # a list to store sent mid
                                            for mid in mentionees:
                                                if mid in sent_mids:  # skip if the mid has already been sent
                                                    continue
                                                _reply = f"@{bot.getContact(mid)[22]}"
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
                                if msg[10].startswith("/userinfo:"):
                                    try:
                                        mlists = []
                                        mentions = bot.getMentioneesByMsgData(msg) or re.findall(
                                            re.compile(r'(?<![a-f0-9])u[a-f0-9]{32}(?![a-f0-9])'), msg[10][10:])
                                        for mention in mentions:
                                            mid = bot.getContact(mention)
                                            if mid[1] not in mlists:
                                                mlists.append(mid[1])
                                        for mlist in mlists:
                                            concact = bot.getContact(mlist)
                                            bot.replyMessage(
                                                msg, f'User Name:\n{concact[22]}\nUser Mid:\n{concact[1]}\nStatus Message:\n{concact[26]}\nProfile Link:\n{bot.LINE_PROFILE_CDN_DOMAIN}/{concact[24] if 24 in concact else "None"}')
                                    except Exception as e:
                                        bot.replyMessage(msg, f'{e.message}')

                                if msg[10] in '/gid':  # get chat room id
                                    bot.replyMessage(msg, msg[2])

                                # get contact via LINE-legy mid or mentions
                                if msg[10].startswith("/getcontact:"):
                                    keys = re.findall(re.compile(
                                        r'(?<![a-f0-9])u[a-f0-9]{32}(?![a-f0-9])'), msg[10][12:])
                                    for key in set(keys):
                                        try:
                                            xmid = bot.getContact(key)[2]
                                            try:
                                                bot.sendContact(
                                                    msg[2], key, "yijhu.xyz")
                                            except Exception as e:
                                                bot.replyMessage(
                                                    msg, f'{e.message}')
                                        except Exception as e:
                                            bot.replyMessage(
                                                msg, f'{e.message}')

                                if msg[10] in '/ginfo':  # get chat room infomation
                                    gid = bot.getChats([msg[2]])[1][0]
                                    g_info = "【Group Info】"
                                    g_info += "\n[Group Name]\n" + gid[6]
                                    g_info += "\n[Group Id]\n" + gid[2]
                                    try:
                                        g_info += "\n[Group Creator]\n" + \
                                            bot.getContact(
                                                gid[8][1][1])[22]
                                    except:
                                        g_info += "\n[Group Creator]\n" + \
                                            bot.getContact(gid[8][1][4][0])[
                                                22] + " (inherit)"
                                    g_info += "\n[Group Profile]\n%s%s" % (
                                        bot.LINE_OBS_DOMAIN, gid[7] if 7 in gid else 'None')
                                    g_info += "\n" + "-" * 40
                                    g_info += " \nMembers： " + \
                                        str(len(gid[8][1][4])) + \
                                        "\nInvitees： " + str(len(gid[8][1][5]))
                                    if gid[8][1][2] is False:
                                        g_info += "\nInvitation Url： Allowed."
                                    else:
                                        g_info += "\nInvitation Url： Blocked."
                                    bot.replyMessage(
                                        msg, f'{g_info}')

                                if msg[10] in '/gowner':
                                    gid = bot.getChats([msg[2]])[1][0]
                                    try:
                                        bot.getContact(gid[8][1][1])[22]
                                        bot.sendContact(
                                            msg[2], gid[8][1][1], "yijhu.xyz")
                                    except:
                                        bot.replyMessage(
                                            msg, "The original group creator has deleted the account.\nThis is the inherited group creator!")
                                        bot.sendContact(
                                            msg[2], gid[8][1][4][0], "yijhu.xyz")

                                if msg[10].startswith("/url:"):  # url:on / off
                                    key = msg[10][5:]
                                    try:
                                        if key.lower() == "on":
                                            bot.updateChatPreventedUrl(
                                                msg[2], False)
                                            uri = bot.reissueChatTicket(msg[2])
                                            bot.replyMessage(
                                                msg, f"https://line.me/R/ti/g/{uri[1]}")
                                        if key.lower() == "off":
                                            bot.reissueChatTicket(msg[2])
                                            bot.updateChatPreventedUrl(
                                                msg[2], True)
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【ERROR】\n{e.message}')

                                if msg[10].startswith("/regname:"):  # regname:str
                                    key = msg[10][9:]
                                    try:
                                        bot.updateChatName(msg[2], key)
                                        bot.replyMessage(
                                            msg, f'【Re GROUP NAME】\n{key}')
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Re GROUP NAME ERROR】\n{e.message}')

                                if msg[10] in '/bye':  # quit bot
                                    bot.replyMessage(msg, "BYE~")
                                    bot.deleteSelfFromChat(msg[2])

                                if msg[10].startswith("/kick:"):  # kick:mid
                                    kmid = re.findall(re.compile(
                                        r'(?<![a-f0-9])u[a-f0-9]{32}(?![a-f0-9])'), msg[10][6:])
                                    klist = []
                                    try:
                                        for someone in kmid:
                                            mid = bot.getContact(someone)
                                            if mid[1] in Owner or mid[1] in Admin or mid[1] in bot.mid:
                                                continue
                                            if someone not in klist:
                                                klist.append(mid[1])
                                            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                                txt = ""
                                                for kmid in klist:
                                                    executor.submit(
                                                        bot.deleteOtherFromChat(msg[2], kmid))
                                                    txt += f"\n．{mid[22]}"
                                        bot.replyMessage(
                                            msg, f'【Kick OUT】{txt}')
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Kick OUT ERROR】\n{e.message}')

                                if msg[10].startswith("/mk:"):  # mk:mentions
                                    klist = []
                                    mentions = bot.getMentioneesByMsgData(msg)
                                    try:
                                        for someone in mentions:
                                            mid = bot.getContact(someone)
                                            if bot.mid in mid[1]:
                                                continue
                                            if mid[1] not in klist:
                                                klist.append(mid[1])
                                                # The limit value of max_workers is 32
                                                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                                    txt = ""
                                                    for kmid in klist:
                                                        executor.submit(
                                                            bot.deleteOtherFromChat(msg[2], kmid))
                                                        txt += f"\n．{mid[22]}"
                                        bot.replyMessage(
                                            msg, f'【Kick OUT】{txt}')
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Kick OUT ERROR】\n{e.message}')

                                if msg[10] in '/cancel':  # cancel all invitation
                                    try:
                                        Invitees = bot.getChats(
                                            [msg[2]])[1][0][8][1][5]
                                        if len(Invitees) == 0:
                                            bot.replyMessage(
                                                msg, "NO Invitation")
                                            continue
                                        # The recommended value of max_workers for this function is 3
                                        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                                            for member in Invitees:
                                                start = time.time()
                                                executor.submit(
                                                    bot.cancelChatInvitation(msg[2], member))
                                                time.sleep(0.8)
                                            end = time.time()
                                            bot.replyMessage(
                                                msg, (end - start))
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f"【Cancel Error】\n{e.message}")

                                if msg[10].startswith("/data:"):  # data:num
                                    num = int(msg[10][6:])+1
                                    try:
                                        data = bot.getRecentMessagesV2(msg[2])[
                                            num-1]
                                        bot.replyMessage(msg, f'{data}')
                                    except Exception as e:
                                        bot.replyMessage(msg, f'{e.message}')

                            if msg[1] in Owner:
                                '''for owner'''
                                if msg[10].startswith("/exec:"):  # cmd:command
                                    command = msg[10][6:]
                                    try:
                                        exec(command)
                                    except Exception as e:
                                        bot.replyMessage(msg, f'{e}')

                                if msg[10].startswith("/rename:"):  # rename:str
                                    key = msg[10][8:]
                                    try:
                                        if len(key) == 0:
                                            bot.replyMessage(
                                                msg, '【Re NAME ERROR】\nCharacter is empty')
                                        else:
                                            bot.updateProfileAttribute(2, key)
                                            bot.replyMessage(
                                                msg, f'【Re NAME】\n{key}')
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Re NAME ERROR】\n{e.message}')

                                if msg[10] in '/repic:':  # repic: file_Path
                                    key = msg[10][7:]
                                    try:
                                        bot.updateProfileImage(key)
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Re PIC ERROR】\n{e.message}')

                                if msg[10].startswith("/rebio:"):  # rebio:str
                                    try:
                                        bio = msg[10][7:]
                                        bot.updateProfileAttribute(16, bio)
                                        bot.replyMessage(
                                            msg[2], f'【Re BIO】\n{bio}')
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【Re BIO ERROR】\n{e.message}')

                                if msg[10] in '/Kickall':  # remove people
                                    klist = bot.getChats([msg[2]])[
                                        1][0][8][1][4]
                                    # The recommended value of max_workers for this function is 15
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                                        start = time.time()
                                        for kmid in klist:
                                            if kmid in Owner or kmid in bot.mid:
                                                continue
                                            executor.submit(
                                                bot.deleteOtherFromChat(msg[2], kmid))
                                        end = time.time()
                                    bot.replyMessage(msg, (end - start))

                                if msg[10] in '/oplist':  # get op list
                                    try:
                                        oplist = "【OP LIST】"
                                        for op in Admin:
                                            oplist += "\n．" + \
                                                bot.getContact(op)[22]
                                        bot.replyMessage(msg, oplist)
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【OP LIST ERROR】\n{e.message}')

                                if msg[10].startswith("/addop:"):  # addop:mentions
                                    try:
                                        mentionees = bot.getMentioneesByMsgData(
                                            msg)
                                        if not mentionees:
                                            bot.replyMessage(
                                                msg, "【ADD ADMIN ERROR】\nPlease Mention the user you want to add.")
                                        with open('./data/auther.json', 'r') as f:
                                            auther = json.load(f)
                                            admin_list = auther.get(
                                                'admin', [])
                                            owner_list = auther.get(
                                                'owner', [])
                                            for mention in mentionees:
                                                mid = mention
                                                if mid not in admin_list or mid not in owner_list:
                                                    admin_list.append(mid)
                                                    Admin.append(mid)
                                            auther['admin'] = admin_list
                                        with open('./data/auther.json', 'w') as f:
                                            json.dump(auther, f, indent=4)
                                        bot.replyMessage(
                                            msg, "Added user as admin!")
                                    except Exception as e:
                                        bot.replyMessage(
                                            msg, f'【ADD ADMIN ERROR】\n{e.message}')

                                    # delop:mentions
                                    if msg[10].startswith("/delop:"):
                                        try:
                                            mentionees = bot.getMentioneesByMsgData(
                                                msg)
                                            if not mentionees:
                                                bot.replyMessage(
                                                    msg, "【REMOVE ADMIN ERROR】\nPlease Mention the user you want to remove.")
                                            with open('./data/auther.json', 'r') as f:
                                                auther = json.load(f)
                                                admin_list = auther.get(
                                                    'admin', [])
                                                for mention in mentionees:
                                                    mid = mention
                                                    if mid in admin_list:
                                                        admin_list.remove(mid)
                                                        Admin.remove(mid)
                                                auther['admin'] = admin_list
                                            with open('./data/auther.json', 'w') as f:
                                                json.dump(auther, f, indent=4)
                                            bot.replyMessage(
                                                msg, "Removed user from admin!")
                                        except Exception as e:
                                            bot.replyMessage(
                                                msg, f'【REMOVE ADMIN ERROR】\n{e.message}')

                    # Not every device is supported. exg:chrome and more...
                    if msg[15] == 6:  # for call
                        if msg[3] == 2:  # for chat room
                            contentMetadata = msg[18]
                            stype = [{"c": "Group "}, {
                                'AUDIO': "Voice Call", 'VIDEO': "Video Call"}]  # type
                            if contentMetadata['GC_MEDIA_TYPE'] in ["AUDIO", "VIDEO"]:
                                type_voices = stype[0][contentMetadata['GC_CHAT_MID']
                                                       [:1]]+stype[1][contentMetadata['GC_MEDIA_TYPE']]
                                if contentMetadata['GC_EVT_TYPE'] == 'S':  # start
                                    bot.sendCompactMessage(msg[2], f"【{type_voices} Start】\nCorrespondent：" + bot.getContact(
                                        msg[1])[22] + "\n" + time.strftime('%Y-%m-%d %I:%M:%S %p'))
                                if contentMetadata['GC_EVT_TYPE'] == 'E':  # end
                                    duration = datetime.timedelta(
                                        milliseconds=int(contentMetadata['DURATION']))
                                    duration_formatted = f"{duration.days}d {duration.seconds//3600}h {duration.seconds//60%60}m {duration.seconds%60}s"
                                    response = f"【{type_voices} Ended】\n[Duration]\n{duration_formatted}\n{time.strftime('%Y-%m-%d %I:%M:%S %p')}"
                                    bot.sendCompactMessage(msg[2], response)

                    if msg[15] == 13:  # for contacts
                        if msg[3] == 2:  # for chatrooms
                            # if msg[1] in Admin:
                            # The limit value of max_workers is 32
                            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                someone = bot.getContact(msg[18]["mid"])
                                executor.submit(bot.sendCompactMessage(msg[2], 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                    someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, someone[24] if 24 in someone else "None")))

                        if msg[3] == 0:  # for chats
                            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                someone = bot.getContact(msg[18]["mid"])
                                # sendChatChecked
                                bot.sendChatChecked(msg[1], msg[4])
                                text = 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                    someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, (someone[24] if 24 in someone else "None"))
                                executor.submit(
                                    bot.sendCompactMessage(msg[1], text))

                    if msg[15] == 14:  # for file
                        if msg[3] == 2:  # for chatrooms
                            contentMetadata = msg[18]
                            ftxt = "【File Info】"
                            if 'FILE_NAME' in contentMetadata:
                                ftxt += "\n[File Name]\n%s" % (
                                    contentMetadata['FILE_NAME'])
                            if 'FILE_SIZE' in contentMetadata:
                                if int(contentMetadata['FILE_SIZE']) <= 1024:
                                    ftxt += "\n[File Size]\n%s B" % (
                                        round(int(contentMetadata['FILE_SIZE']), 1))
                                elif int(contentMetadata['FILE_SIZE']) <= 1048576:
                                    ftxt += "\n[File Size]\n%s KB" % (
                                        round(int(contentMetadata['FILE_SIZE'])/1024, 1))
                                elif int(contentMetadata['FILE_SIZE']) <= 1073741824:
                                    ftxt += "\n[File Size]\n%s MB" % (
                                        round(int(contentMetadata['FILE_SIZE'])/1048576, 1))
                                else:
                                    ftxt += "\n[File Size]\n%s GB" % (
                                        round(int(contentMetadata['FILE_SIZE'])/1073741824, 1))
                            if 'FILE_EXPIRE_TIMESTAMP' in contentMetadata:
                                ftxt += "\n[File Expire time]\n%s" % (time.strftime(
                                    '%Y-%m-%d %I:%M:%S %p', time.localtime(int(contentMetadata['FILE_EXPIRE_TIMESTAMP'])/1000)))
                            bot.sendCompactMessage(msg[2], ftxt)

                    if msg[15] == 16:  # for post notification
                        if msg[3] == 2:  # for chatrooms
                            contentMetadata = msg[18]
                            if contentMetadata['serviceType'] == 'GB':  # group post
                                g_post = "【Group Post Info】"
                                g_post += "\n[Post Owner]\n" + \
                                    bot.getContact(msg[1])[22]
                                if 'text' in contentMetadata:
                                    g_post += "\n[Post Preview]\n%s" % (
                                        contentMetadata['text'])
                                if 'mediaOid' in contentMetadata:
                                    if contentMetadata['mediaType'] == 'I':  # Image
                                        g_post += "\n[Media Url]\n%s/r/myhome/h/%s" % (
                                            bot.LINE_OBS_DOMAIN, contentMetadata['mediaOid'])
                                    elif contentMetadata['mediaType'] == 'V':  # Video
                                        g_post += "\n[Media Url]\n%s/r/myhome/h/%s" % (
                                            bot.LINE_OBS_DOMAIN, contentMetadata['mediaOid'])
                                if 'locationName' in contentMetadata:
                                    g_post += "\n[Location Name]\n%s" % (
                                        contentMetadata['locationName'])
                                if 'location' in contentMetadata:
                                    g_post += "\n[Location]\n%s" % (
                                        contentMetadata['location'])
                                g_post += "\n[Post Url]\n%s" % (
                                    contentMetadata['postEndUrl'])
                                bot.replyMessage(msg, g_post)

                            if contentMetadata['serviceType'] == 'MH':  # personal post
                                p_post = "【Post Info】"
                                if 'serviceName' in contentMetadata:
                                    p_post += "\n[Post Owner]\n%s" % (
                                        contentMetadata['serviceName'])
                                if 'text' in contentMetadata:
                                    p_post += "\n[Post Preview]\n%s" % (
                                        contentMetadata['text'])
                                if 'mediaOid' in contentMetadata:
                                    mediaOid = contentMetadata['mediaOid'].replace(
                                        "svc=", "/").replace("|sid=", "/").replace("|oid=", "/")
                                    if contentMetadata['mediaType'] == 'I':
                                        p_post += "\n[Media Url]\n%s/r%s" % (
                                            bot.LINE_OBS_DOMAIN, mediaOid)
                                    elif contentMetadata['mediaType'] == 'V':
                                        p_post += "\n[Media Url]\n%s/r%s" % (
                                            bot.LINE_OBS_DOMAIN, mediaOid)
                                if 'locationName' in contentMetadata:
                                    p_post += "\n[Location Name]\n%s" % (
                                        contentMetadata['locationName'])
                                if "location" in contentMetadata:
                                    p_post += "\n[Location]\n" + \
                                        contentMetadata["location"]
                                p_post += "\n[Post Url]\n" + \
                                    contentMetadata["postEndUrl"]
                                bot.sendCompactMessage(msg[2], p_post)

                            if contentMetadata['serviceType'] == 'AB':  # album
                                if contentMetadata['locKey'] == 'BA':  # creat album
                                    album = "【Group Album】"
                                    album += "\n[Photo Sender]\n%s" % (
                                        bot.getContact(msg[1])[22])
                                    if 'albumName' in contentMetadata:
                                        album += "\n[Album Name]\n%s" % (
                                            contentMetadata['albumName'])
                                    if 'mediaCount' in contentMetadata:
                                        album += "\n[Photo Count]\n%s" % (
                                            int(contentMetadata['mediaCount'])+1)
                                    album += "\n[Album Url]\n%s" % (
                                        contentMetadata['postEndUrl'].replace("line://", "https://line.me/R/"))
                                    bot.replyMessage(msg, album)
                                if contentMetadata['locKey'] == 'BT':  # add photos
                                    album = "【Group Album】"
                                    album += "\n[Photo Sender]\n%s" % (
                                        bot.getContact(msg[1])[22])
                                    if 'albumName' in contentMetadata:
                                        album += "\n[Album Name]\n%s" % (
                                            contentMetadata['albumName'])
                                    if 'mediaCount' in contentMetadata:
                                        album += "\n[Photo Count]\n%s" % (
                                            int(contentMetadata['mediaCount'])+1)
                                    album += "\n[Album Url]\n%s" % (
                                        contentMetadata['postEndUrl'].replace("line://", "https://line.me/R/"))
                                    bot.replyMessage(msg, album)

                    if msg[15] == 18:  # for chat event
                        try:
                            if msg[3] == 2:
                                contentMetadata = msg[18]
                                event_type = contentMetadata['LOC_KEY']
                                contact_name = bot.getContact(msg[1])[22]
                                album_name = contentMetadata['LOC_ARGS']
                                if event_type == 'BD':
                                    message = f"【Deleted Album】\n[Deleted Person]\n{contact_name}\n[Album Name]\n{album_name}"
                                elif event_type == 'BO':
                                    message = f"【Deleted Photo】\n[Deleted Person]\n{contact_name}\n[Album Name]\n{album_name}"
                                elif event_type == 'BB':
                                    old_name, new_name = album_name.split(
                                        "\x1e")
                                    message = f"【Changed Album Name】\n[Changed Person]\n{contact_name}\n[Old Name] ==> {old_name}\n[New Name] ==> {new_name}"
                                bot.sendCompactMessage(msg[2], message)
                        except Exception as e:
                            bot.log(f'Chat Event Error: {e}')

                except Exception as e:
                    bot.log(f'Receive Message Error: {e}')

            if op[3] == 124 and bot.mid in op[12]:  # for notifed invite to chat
                try:
                    bot.acceptChatInvitation(op[10])
                    if op[11] in Admin or op[11] in Owner:
                        bot.sendCompactMessage(
                            op[10], 'THANKS FOR USING.\n[Author Page]\nhttps://profile.yijhu.xyz/\n[Open source]\nhttps://github.com/YiJhu/Aria_helper/\n[Privacy Policy]\nhttps://yijhu.xyz/privacy/\n[Support this project]\nhttps://ko-fi.com/archibald_tw')
                    else:
                        bot.sendCompactMessage(
                            op[10], 'NO PERMISSION.\n[Author Page]\nhttps://profile.yijhu.xyz/\n[Open source]\nhttps://github.com/YiJhu/Aria_helper/\n[Privacy Policy]\nhttps://yijhu.xyz/privacy/\n[Support this project]\nhttps://ko-fi.com/archibald_tw')
                        bot.deleteSelfFromChat(op[10])
                        # bot.rejectChatInvitation(op[10])
                except Exception as e:
                    bot.log(f'Notified Invite To Chat Error: {e.message}')

            if op[3] == 127:  # for delete self from chat
                try:
                    if op[10] in bot.groups:
                        bot.groups.remove(op[10])
                except Exception as e:
                    bot.log(f'Delete Self From Chat Error: {e.message}')

            if op[3] == 129:  # for accept chat invitation
                try:
                    if op[10] not in bot.groups:
                        bot.groups.append(op[10])
                except Exception as e:
                    bot.log(f'Accept Chat Invitation Error: {e.message}')

            if op[3] == 133:  # for notifed delete other from chat
                try:
                    if op[10] in bot.groups and op[12] in bot.mid:
                        bot.groups.remove(op[10])
                    bot.log(f'{op[11]} kicked {op[12]} from {op[10]}')
                except Exception as e:
                    bot.log(
                        f'Notified Delete Other From Chat Error: {e.message}')

            if op[3] == 5:  # for notifed add contact
                try:
                    text = f"Hi {bot.getContact(op[10])[22]} Thanks Add Me.\nMy creator is: L.H.\n[Author Page]\nhttps://profile.yijhu.xyz/\n\n[Privacy Policy]\nhttps://yijhu.xyz/privacy/\n[Support this project]\nko-fi\nhttps://ko-fi.com/archibald_tw\nPayPal\nwww.paypal.me/YiJhu486\n街口支付(JKO Pay)\nhttps://www.jkopay.com/transfer?j=Transfer:908589779"
                    bot.sendCompactMessage(op[10], text)
                except Exception as e:
                    bot.log(f'Notified Add Contact Error: {e.message}')
