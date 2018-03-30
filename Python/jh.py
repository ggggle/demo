#!/usr/bin/python
#-*- coding:utf-8 -*-
import pexpect
import readline, rlcompleter; readline.parse_and_bind("tab: complete")

'''***must edit in script***'''
ftpasswd_path = '/var/proftpd/bin/'   #ftpasswd binary file path
home = '/home'                        #ftp home folder

'''Can use '4' operate to load from file or Just change at here, as you like'''
auth_path = ''
useredit_file = ''
grpedit_file = ''
proftpd_cfg_path = '/etc/proftpd.conf'
userinfo_file = '/etc/proftpd/passwd'
grpinfo_file = '/etc/proftpd/group'

'''Don't touch it if you don't know it'''
uid = '8549'
gid = '9540'
usershell = '/sbin/nologin'

default_mod = '''<Directory %s/*>
    HideNoAccess on
    <Limit All>
        DenyAll
        AllowGroup Manager
    </Limit>
</Directory>

''' % home


def outlog(log):
    print(log)


def create_user(username, passwd, userhome, uid, file_path, usershell):
    cmd = '%sftpasswd --passwd --file=%s --name=%s --uid=%s --home=%s --shell=%s --stdin' % \
          (ftpasswd_path, file_path, username, uid, userhome, usershell)
    #print(cmd)
    child = pexpect.spawn(cmd)
    #child.logfile = sys.stdout
    index = child.expect(["ftpasswd: creating passwd", "ftpasswd: updating passwd", pexpect.EOF, pexpect.TIMEOUT], timeout=2)
    if index == 0 or index == 1:
        child.sendline(passwd)
        index = child.expect(["ftpasswd: entry created", "ftpasswd: entry updated", pexpect.EOF, pexpect.TIMEOUT], timeout=2)
        if index == 0:
            outlog('success created (%s)!' % username)
            return 0
        elif index == 1:
            outlog('**username (%s) already exist, update passwd success**' % username)
            return 1
        elif index == 2:
            outlog('-----At Second Input EOF-----')
        elif index == 3:
            outlog('-----At Second Input TimeOut-----')
    elif index == 2:
        outlog('-----At CMD EOF-----')
    elif index == 3:
        outlog('-----At CMD TimeOut-----')
    return -1


def create_group(groupname, gid, member_list, file_path):
    member_cmd = ''
    for item in member_list:
        member_cmd+=(' --member=' + item)
    cmd = '%sftpasswd --group --name=%s --gid=%s --file=%s%s' % (ftpasswd_path, groupname, gid, file_path, member_cmd)
    #print(cmd)
    child = pexpect.spawn(cmd)
    index = child.expect(["ftpasswd: entry created", "ftpasswd: entry updated", pexpect.EOF, pexpect.TIMEOUT], timeout=2)
    if index == 0:
        outlog("success created group (%s)" % groupname)
        return 0
    elif index == 1:
        outlog("**group (%s) already exist, update group info success**" % groupname)
        return 1
    elif index == 2:
        outlog('-----Create Group EOF-----')
    elif index == 3:
        outlog('-----Create Group TimeOut-----')


def create_user_from_file(path):
    user_list = []
    try:
        file = open(path)
    except IOError:
        print('#(%s)no such file or it is a directory#' % path)
        return -1
    for line in file:
        if line != '\n':
            user_list.append(line.rstrip('\n'))
    for item in user_list:
        item_split = item.split()
        create_user(username=item_split[0], passwd=item_split[1], userhome=home, uid=uid,
                    file_path=userinfo_file, usershell=usershell)


def create_group_from_file():
    try:
        file = open(grpedit_file)
    except IOError:
        print('#(%s)no such file or it is a directory#' % grpedit_file)
        return -1
    for line in file:
        if line != '\n':
            line = line.rstrip('\n')
            line_split = line.split()
            user_list = line_split[1].split(',')
            #grpid = line_split[1]
            grpname = line_split[0]
            create_group(groupname=grpname, gid=gid, member_list=user_list, file_path=grpinfo_file)


'''加载脚本配置文件，现在主要有两条，一是用户信息存储文件路径，二是组信息存储文件路径'''
def load_config(config_path='script.cfg'):
    cfg_dict = {}
    global proftpd_cfg_path, auth_path, userinfo_file, grpinfo_file ,useredit_file, grpedit_file
    try:
        cfg_file = open(config_path)
    except IOError:
        print('#(%s)no such file or it is a directory#' % config_path)
        return -1
    for line in cfg_file:
        line = line.rstrip('\n')
        line_split = line.split('=')
        cfg_dict[line_split[0]] = line_split[1]
    try:
        proftpd_cfg_path = cfg_dict['proftpd_cfg_path']
        print("**success set proftpd_cfg_path(%s)**" % cfg_dict['proftpd_cfg_path'])
    except:
        pass
    try:
        auth_path = cfg_dict['auth_path']
        print("**success set proftpd_cfg_path(%s)**" % cfg_dict['proftpd_cfg_path'])
    except:
        pass
    try:
        userinfo_file = cfg_dict['userinfo_file']
        print("**success set userinfo_file(%s)**" % cfg_dict['userinfo_file'])
    except:
        pass
    try:
        grpinfo_file = cfg_dict['grpinfo_file']
        print("**success set grpinfo_file(%s)**" % cfg_dict['grpinfo_file'])
    except:
        pass
    try:
        useredit_file = cfg_dict['useredit_file']
        print("**success set useredit_file(%s)**" % cfg_dict['useredit_file'])
    except:
        pass
    try:
        grpedit_file = cfg_dict['grpedit_file']
        print("**success set grpedit_file(%s)**" % cfg_dict['grpedit_file'])
    except:
        pass


def allow_group(object="DIRS READ", groupstr=""):
    str = '''<Limit %s>
        AllowGroup OR %s
    </Limit>''' % (object, groupstr)
    return str


def dst_dict(dict, allowgrp_format):
    str = '''<Directory %s>
    %s
</Directory>''' % (dict, allowgrp_format)
    return str


'''根据给定的组文件夹权限配置，生成并返回配置字符串'''
def make_proftpd_cfg(path):
    try:
        file = open(path)
    except IOError:
        print('#(%s)no such file or it is a directory#' % path)
        return -1
    auth_dict = {}
    for line in file:
        if line != '\n':
            line = line.rstrip('\n')
            line_split = line.split()
            for item in line_split[1].split(','):
                try:
                    if auth_dict[item] == None:
                        pass
                    else:
                        auth_dict[item] += ','
                except KeyError:
                    auth_dict[item] = ''
                auth_dict[item] += line_split[0]
    resultstr = ''
    resultstr += "############auto make limit cfg############\n"
    resultstr += default_mod
    for key in auth_dict.keys():
        str = dst_dict(key, allow_group(groupstr=auth_dict[key]))
        resultstr += (str+'\n'*2)
    return resultstr


def write_cfg():
    try:
        old_cfg = open(proftpd_cfg_path)
    except IOError:
        print('#(%s)no such file or it is a directory#' % proftpd_cfg_path)
        return -1
    old_str = ''
    for line in old_cfg:
        line = line.rstrip('\n')
        if line != '############auto make limit cfg############':
            old_str += (line + '\n')
        else:
            break
    old_cfg.close()
    new_str = old_str + make_proftpd_cfg(auth_path)
    new_cfg = open(proftpd_cfg_path, 'w')
    new_cfg.write(new_str)
    new_cfg.close()
    return 0


def main():
    if home == '' or ftpasswd_path == '':
        print("@@@Please edit the script file ， input the 'ftpasswd_path' and 'home'@@@")
        return
    show_info = '''---------------------------------------------------------------
|1.Create user or update password
|2.Create group or update group infomation
|3.Change group can access folder and write into proftpd.conf
|4.Reload script config from file(ex. AuthUserFile path | 'proftpd.conf' path and more)
---------------------------------------------------------------'''
    try:
        while True:
            print(show_info)
            try:
                select = raw_input("Enter you select:")
            except:
                print('\nbye')
                return
            select = str(select)
            if select == '1':
                global userinfo_file, useredit_file
                try:
                    flag = raw_input("Input user information file path:(default %s)" % useredit_file)
                    if flag != '':
                        useredit_file = flag
                    flag = raw_input("Input the AuthUserFile path:(default %s)" % userinfo_file)
                    if flag != '':
                        userinfo_file = flag
                except KeyboardInterrupt:
                    print('\nbye')
                    return
                create_user_from_file(useredit_file)
            elif select == '2':
                global grpinfo_file, grpedit_file
                try:
                    flag = raw_input("Input group information file path:(default %s)" % grpedit_file)
                    if flag != '':
                        grpedit_file = flag
                    flag = raw_input("Input the AuthGroupFile path:(default %s)" % grpinfo_file)
                    if flag != '':
                        grpinfo_file = flag
                except KeyboardInterrupt:
                    print('\nbye')
                    return
                create_group_from_file()
            elif select == '3':
                global proftpd_cfg_path, auth_path
                try:
                    flag = raw_input("Input auth file:(default %s)" % auth_path)
                    if flag != '':
                        auth_path = flag
                    flag = raw_input("Input the 'proftpd.conf' path(default %s)" % proftpd_cfg_path)
                    if flag != '':
                        proftpd_cfg_path = flag
                except KeyboardInterrupt:
                    print('\nbye')
                    return
                result = write_cfg()
                if result != 0:
                    print("#there is some error#")
                else:
                    print("**success update the %s**" % proftpd_cfg_path)
            elif select == '4':
                try:
                    script_cfg = raw_input("Input script cfg path:")
                except KeyboardInterrupt:
                    print('\nbye')
                    return
                load_config(script_cfg)
            else:
                print("#Please enter the right number.#")
    except KeyboardInterrupt:
        print('\nbye')
        return


if __name__ == "__main__":
    main()