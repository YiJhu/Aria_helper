#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
    This is a main program in Aria helper CHRLINE Version.
    Versoin: CHR_Aria 1.2
    Auther: YiJhu (https://github.com/yijhu/)
    Web: (https://profile.yijhu.xyz)
    ------------------------------------------------------
    Library: CHRLINE (ver: 2.5.1)
'''
from CHRLINE import *
import time
import timeit
import concurrent
import base64

bot = CHRLINE(authTokenOrEmail="Token or mail", password="Password",
              device="DESKTOPWIN", os_name="Aria helper", useThrift=False)

Admin = ["Admin_MID"]  # Admin
Owner = ["Owner_MID"]  # Owner

rev = 0
# rev = bot.getLastOpRevision()

helplist = "#help\n#speed\n#time\n#me\n#mid\n#mid:@{byTag}\n#userinfo:@{byTag}\n#gid\n#getcontact:{mid}\n#tagcontact:@{byTag}\n#ginfo\n#gowner\n#url:{on/off}\n#regname:{new group name}\n#bye\n#kick:{mid}\n#mk:@{byTag}\n#cancel\n#data:{num}"

while True:
    Ops = bot.fetchOps(rev)
    for op in Ops:
        if op and 0 not in op and op[3] != 0:
            rev = max(rev, op[1])
            # print('%s\n\n' % (op))
            if op[3] == 26:
                msg = op[20]
                if msg[15] == 0:
                    if msg[3] == 2:
                        if msg[1] in Owner or msg[1] in Admin:
                            if msg[10] == '#help':  # help commands
                                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                    help = str(helplist)
                                    if msg[1] in Owner:
                                        help += str(
                                            "\n#exec:{text}\n#rename:{text}\n#rebio:{text}\n#repic:{path}\n#Kickall")
                                    else:
                                        continue
                                    executor.submit(bot.replyMessage(
                                        msg, f"【HELP COMMAND】\n{help}"))

                            if msg[10] == '#speed':  # speed test
                                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                    speed = timeit.timeit(
                                        '"-".join(str(n) for n in range(100))', number=10000)
                                    executor.submit(bot.replyMessage(
                                        msg, f"SpeedTest： {speed} s"))

                            if msg[10] == '#time':  # get time
                                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                    stime = bot.getServerTime()
                                    executor.submit(bot.replyMessage(msg,  "【Now Time (UTC+8)】\n" + time.strftime(
                                        '%Y-%m-%d %I:%M:%S %p', time.localtime(stime/1000))))

                            if msg[10] == '#me':  # get your contact
                                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                    executor.submit(bot.sendContact(
                                        msg[2], msg[1], "yijhu.xyz"))

                            if msg[10] == '#mid':  # get your LINE-legy mid
                                bot.replyMessage(msg, msg[1])

                            # get user LINE-legy mid via mentionees
                            if msg[10].startswith("#mid:"):
                                mlists = []
                                if 'MENTION' in msg[18]:
                                    key = eval(msg[18]["MENTION"])
                                    tags = key["MENTIONEES"]
                                    for tag in tags:
                                        mid = bot.getContact(tag['M'])
                                        if mid[1] not in mlists:
                                            mlists.append(mid[1])
                                        txt = ""
                                    for mlist in mlists:
                                        n = bot.getContact(mlist)
                                        txt += f"{n[22]}\n"
                                        txt += f"{n[1]}\n"
                                bot.replyMessage(msg, txt)
                                del mlists

                            # get user infomation via mentionees
                            if msg[10].startswith("#userinfo:"):
                                mlists = []
                                if 'MENTION' in msg[18]:
                                    key = eval(msg[18]["MENTION"])
                                    tags = key["MENTIONEES"]
                                    for tag in tags:
                                        mid = bot.getContact(tag['M'])
                                        if mid[1] not in mlists:
                                            mlists.append(mid[1])
                                    for mlist in mlists:
                                        concact = bot.getContact(mlist)
                                        try:
                                            bot.replyMessage(msg, 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n%s\nProfile Link:\n%s/%s' % (
                                                concact[22], concact[1], concact[26], bot.LINE_PROFILE_CDN_DOMAIN, concact[24]))
                                        except:
                                            bot.replyMessage(msg, 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n%s\nProfile Link:\n%s/%s' % (
                                                concact[22], concact[1], concact[26], bot.LINE_PROFILE_CDN_DOMAIN, 'None'))

                            if msg[10] == '#gid':  # get chat room id
                                bot.replyMessage(msg, msg[2])

                            # get contact via LINE-legy mid
                            if msg[10].startswith("#getcontact:"):
                                key = msg[10][12:]
                                if len(key) <= 32:
                                    bot.replyMessage(
                                        msg, '【MID ERROR】\nCharacter is empty')
                                else:
                                    try:
                                        xmid = bot.getContact(key)[2]
                                        try:
                                            bot.sendContact(
                                                msg[2], key, "yijhu.xyz")
                                        except:
                                            pass
                                    except:
                                        bot.replyMessage(
                                            msg, '【MID ERROR】\nNo such user')

                            # tagcontact: mentions
                            # get contact via mentions
                            if msg[10].startswith("#tagcontact:"):
                                mlists = []
                                if 'MENTION' in msg[18]:
                                    key = eval(msg[18]["MENTION"])
                                    tags = key["MENTIONEES"]
                                    for tag in tags:
                                        mid = bot.getContact(tag['M'])
                                        if mid[1] not in mlists:
                                            mlists.append(mid[1])
                                    for mlist in mlists:
                                        bot.sendContact(
                                            msg[2], mlist, "yijhu.xyz")
                                del mlists

                            if msg[10] == '#ginfo':  # get chat room infomation
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
                                try:
                                    g_info += "\n[Group Profile]\n%s%s" % (
                                        bot.LINE_OBS_DOMAIN, gid[7])
                                except:
                                    g_info += "\n[Group Profile]\n%s/%s" % (
                                        bot.LINE_OBS_DOMAIN, 'None')
                                g_info += "\n[Created Time]\n" + time.strftime(
                                    '%Y-%m-%d %I:%M:%S %p', time.localtime(gid[3]/1000))
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

                            if msg[10] == '#gowner':
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

                            if msg[10].startswith("#url:"):  # url:on / off
                                key = msg[10][5:]
                                if key.lower() == "on":
                                    bot.updateChatPreventedUrl(msg[2], False)
                                    uri = bot.reissueChatTicket(msg[2])
                                    bot.replyMessage(
                                        msg, f"https://line.me/R/ti/g/{uri[1]}")
                                if key.lower() == "off":
                                    bot.reissueChatTicket(msg[2])
                                    bot.updateChatPreventedUrl(msg[2], True)

                            if msg[10].startswith("#regname:"):  # regname:str
                                key = msg[10][9:]
                                bot.updateChatName(msg[2], key)
                                bot.replyMessage(
                                    msg, f'【Re GROUP NAME】\n{key}')

                            if msg[10] == '#bye':  # quit bot
                                bot.replyMessage(msg, "BYE~")
                                bot.deleteSelfFromChat(msg[2])

                            if msg[10].startswith("#kick:"):  # kick:mid
                                kmid = msg[10][6:]
                                if len(kmid) <= 32:
                                    pass
                                else:
                                    try:
                                        if bot.profile[1] == kmid:
                                            continue
                                        bot.deleteOtherFromChat(msg[2], kmid)
                                        xname = bot.getContact(f'{kmid}')
                                        bot.replyMessage(
                                            msg, '【Kick OUT】\n' + xname[22])
                                    except:
                                        pass

                            if msg[10].startswith("#mk:"):  # mk:mentions
                                klist = []
                                if 'MENTION' in msg[18]:
                                    key = eval(msg[18]["MENTION"])
                                    tags = key["MENTIONEES"]
                                    for tag in tags:
                                        mid = bot.getContact(tag['M'])
                                        if bot.profile[1] in mid[1]:
                                            continue
                                        if mid[1] not in klist:
                                            klist.append(mid[1])
                                            # The limit value of max_workers is 32
                                            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                                                for kmid in klist:
                                                    executor.submit(
                                                        bot.deleteOtherFromChat(msg[2], kmid))
                                                    txt = ""
                                                    txt += mid[22]
                                        bot.replyMessage(
                                            msg, f'【Kick OUT】\n{txt}')
                                del klist

                            if msg[10] == '#cancel':  # cancel all invitation
                                try:
                                    Invitees = bot.getChats(
                                        [msg[2]])[1][0][8][1][5]
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
                                except:
                                    bot.replyMessage(
                                        msg, "NO Invitation")

                            if msg[10].startswith("#data:"):  # data:num
                                num = int(msg[10][6:])+1
                                try:
                                    data = bot.getRecentMessagesV2(msg[2])[
                                        num-1]
                                    bot.replyMessage(msg, f'{data}')
                                except Exception as e:
                                    bot.replyMessage(msg, f'{e}')
                        if msg[1] in Owner:
                            '''for owner'''
                            if msg[10].startswith("#exec:"):  # cmd:command
                                command = msg[10][6:]
                                try:
                                    exec(command)
                                except Exception as e:
                                    bot.replyMessage(msg, f'{e}')

                            if msg[10].startswith("#rename:"):  # rename:str
                                key = msg[10][8:]
                                if len(key) == 0:
                                    bot.replyMessage(
                                        msg, '【Re NAME ERROR】\nCharacter is empty')
                                else:
                                    bot.updateProfileAttribute(2, key)
                                    bot.replyMessage(
                                        msg, f'【Re NAME】\n{key}')

                            if msg[10] == '#repic:':  # repic: file_Path
                                key = msg[10][7:]
                                bot.updateProfileImage(key)

                            if msg[10].startswith("#rebio:"):  # rebio:str
                                bio = msg[10][7:]
                                bot.updateProfileAttribute(16, bio)
                                bot.replyMessage(
                                    msg[2], f'【Re BIO】\n{bio}')

                            if msg[10] == '#Kickall':  # remove people
                                klist = bot.getChats([msg[2]])[1][0][8][1][4]
                                # The recommended value of max_workers for this function is 15
                                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                                    start = time.time()
                                    for kmid in klist:
                                        if kmid in Owner or kmid in bot.profile[1]:
                                            continue
                                        executor.submit(
                                            bot.deleteOtherFromChat(msg[2], kmid))
                                    end = time.time()
                                bot.replyMessage(msg, (end - start))

                # call
                # Not every device is supported. exg:chrome and more...
                if msg[15] == 6:
                    if msg[3] == 2:  # for chat room
                        contentMetadata = msg[18]
                        stype = [{"r": "Room ", "c": "Group "}, {
                            'AUDIO': "Voice Call", 'VIDEO': "Video Call"}]  # type
                        if contentMetadata['GC_MEDIA_TYPE'] in ["AUDIO", "VIDEO"]:
                            type_voices = stype[0][contentMetadata['GC_CHAT_MID']
                                                   [:1]]+stype[1][contentMetadata['GC_MEDIA_TYPE']]
                            if contentMetadata['GC_EVT_TYPE'] == 'S':  # start
                                bot.sendCompactMessage(msg[2], "【" + type_voices + " Start】\nCorrespondent：" + bot.getContact(
                                    msg[1])[22] + "\n" + time.strftime('%H:%M:%S'))
                            if contentMetadata['GC_EVT_TYPE'] == 'E':  # end
                                pass

                if msg[15] == 13:  # user infomation
                    if msg[3] == 2:  # for chat room
                        # if msg[1] in Admin:
                        # The limit value of max_workers is 32
                        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                            someone = bot.getContact(msg[18]["mid"])
                            try:
                                executor.submit(bot.sendCompactMessage(msg[2], 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                    someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, someone[24])))
                            except:
                                executor.submit(bot.sendCompactMessage(msg[2], 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                    someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, 'None')))
                    if msg[3] == 0:  # for chat
                        someone = bot.getContact(msg[18]["mid"])
                        bot.sendChatChecked(msg[1], msg[4])
                        selfKeyData = bot.getE2EESelfKeyData(bot.mid)
                        senderKeyId = selfKeyData['keyId']
                        private_key = base64.b64decode(selfKeyData['privKey'])
                        receiver_key_data = bot.negotiateE2EEPublicKey(msg[1])
                        if receiver_key_data[3] == -1:
                            raise Exception(f'Not support E2EE on {msg[1]}')
                        receiverKeyId = receiver_key_data[2][2]
                        keyData = bot.generateSharedSecret(
                            bytes(private_key), receiver_key_data[2][4])
                        specVersion = receiver_key_data[3]
                        try:
                            text = 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, someone[24])
                            encData = bot.encryptE2EETextMessage(
                                senderKeyId, receiverKeyId, keyData, specVersion, text, msg[1], bot.mid)
                            bot.sendMessageWithChunks(
                                msg[1], encData, 0, {'e2eeVersion': '2', 'contentType': '0'})
                        except:
                            text = 'User Name:\n%s\nUser Mid:\n%s\nStatus Message:\n(Only show 100 words!)\n%s\nProfile Link:\n%s/%s' % (
                                someone[22], someone[1], someone[26][:100], bot.LINE_PROFILE_CDN_DOMAIN, 'None')
                            encData = bot.encryptE2EETextMessage(
                                senderKeyId, receiverKeyId, keyData, specVersion, text, msg[1], bot.mid)
                            bot.sendMessageWithChunks(
                                msg[1], encData, 0, {'e2eeVersion': '2', 'contentType': '0'})

                if msg[15] == 14:  # file infomation
                    if msg[3] == 2:
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

                if msg[15] == 16:
                    if msg[3] == 2:
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
                                stra = contentMetadata['mediaOid'].replace(
                                    "svc=", "/")
                                strb = stra.replace("|sid=", "/")
                                mediaOid = strb.replace("|oid=", "/")
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
                                bot.sendCompactMessage(msg[2], album)
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
                                bot.sendCompactMessage(msg[2], album)

                if msg[15] == 18:  # del Album or photo or inv_someone or cancel_someone
                    pass

            if op[3] == 124 and bot.profile[1] in op[12]:
                try:
                    bot.acceptChatInvitation(op[10])
                    if op[11] in Admin or op[11] in Owner:
                        bot.sendCompactMessage(op[10], 'THANKS FOR USEING.')
                    else:
                        bot.sendCompactMessage(op[10], 'No PERMISSION.')
                        bot.deleteSelfFromChat(op[10])
                        # bot.rejectChatInvitation(op[10])
                except:
                    continue
