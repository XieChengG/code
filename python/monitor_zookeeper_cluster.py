import sys
import socket
import subprocess
from StringIO import StringIO
import os

zabbix_sender = "/app/zabbix/bin/zabbix-sender"
zabbix_conf = "/app/zabbix/conf/zabbix.conf"
send_to_zabbix = 1


class ZookeeperServer(object):
    def __init__(self, host='localhost', port='2181', timeout=1):
        self._address = (host, int(port))
        self._timeout = timeout
        self._result = {}

    def _create_socket(self):
        return socket.socket()

    def _send_cmd(self, cmd):
        s = self._create_socket()
        s.settimeout(self._timeout)
        s.connect(self._address)
        s.send(cmd)
        data = s.recv(1024)
        s.close()
        return data

    def get_stats(self):
        data_mntr = self._send_cmd('mntr')
        data_ruok = self._send_cmd('ruok')
        if data_mntr:
            result_mntr = self._parse(data_mntr)
        if data_ruok:
            result_ruok = self._parse_ruok(data_ruok)
        self._result = dict(result_mntr.items() + result_ruok.items())
        if not self._result.has_key('zk_followers') and not self._result.has_key(
                'zk_synced_followers') and not self._result.has_key('zk_pending_syncs'):
            leader_only = {'zk_followers': 0, 'zk_synced_followers': 0, 'zk_pending_syncs': 0}
            self._result = dict(result_mntr.items() + result_ruok.items() + leader_only.items())
        return self._result

    def _parse(self, data):
        h = StringIO(data)
        result = {}
        for line in h.readlines():
            try:
                key, value = self._parse_line(line)
                result[key] = value
            except ValueError:
                pass
        return result

    def _parse_ruok(self, data):
        h = StringIO(data)
        result = {}
        ruok = h.readline()
        if ruok:
            result['zk_server_ruok'] = ruok
        return result

    def _parse_line(self, line):
        try:
            key, value = map(str.strip, line.split('\t'))
        except ValueError:
            raise ValueError('Found invalid line: {}'.format(line.strip()))
        if not key:
            raise ValueError('The key is mandatory and should not be empty')

        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
        return key, value

    def get_pid(self):
        arg_dict = {}
        pid_arg = 'echo mntr | nc 127.0.0.1 2181'
        pid_out = subprocess.Popen(pid_arg, shell=True, stdout=subprocess.PIPE)
        line = pid_out.stdout.readline().strip('\n')
        while line:
            al = line.split('\t')
            if al[0] == 'zk_version':
                value = al[1][:al[1].find('-')]
                arg_dict[al[0]] = value
            else:
                arg_dict[al[0]] = al[1]
            line = pid_out.stdout.readline().strip('\n')

        pid_arg = 'echo srvr | nc 127.0.0.1 2181'
        pid_out = subprocess.Popen(pid_arg, shell=True, stdout=subprocess.PIPE)
        line = pid_out.stdout.readline().strip('\n')
        while line:
            al = line.split(':')
            arg_dict[al[0].strip()] = al[1].strip()
            line = pid_out.stdout.readline().strip('\n')

        pid_arg = 'echo ruok | nc 127.0.0.1 2181'
        pid_out = subprocess.Popen(pid_arg, shell=True, stdout=subprocess.PIPE)
        line = pid_out.stdout.readline().strip('\n')
        arg_dict['ruok'] = line

        pid_arg = "ps -ef |grep java |grep zookeeper |grep -v grep |awk '{print $2}'"
        pid_out = subprocess.Popen(pid_arg, shell=True, stdout=subprocess.PIPE)
        line = pid_out.stdout.readline().strip('\n')
        arg_dict['all'] = line
        arg_dict['alive'] = line
        return arg_dict


def usage():
    print("\nUsage: ", sys.argv[0], " alive|all")
    print("Modes: \n\talive: Return pid of running zookeeper\n\tall: Send zookeeper stats as well")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        mode = sys.argv[1]
    else:
        usage()

    zk = ZookeeperServer()
    pid = zk.get_pid()
    if pid and mode in pid.keys():
        print(pid.get(mode))
