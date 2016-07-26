#!/usr/bin/env python
# -*- coding:utf8 -*-
import os,sys
import requests
import socket
import yaml

reload(sys)
sys.setdefaultencoding("utf8")


def logger():
    import logging
    LOG_FORMAT = "[%(asctime)s]\t[%(levelname)s]\t[%(message)s]"
    LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.txt")
    logging.basicConfig(format = LOG_FORMAT, level = logging.DEBUG, filename = LOG_FILE)
    return logging.getLogger(__name__)


def getopts():
    import argparse
    parser = argparse.ArgumentParser(description = 'github.com/migege/dnspod')
    parser.add_argument('config', help = 'config file in yaml')
    opts = parser.parse_args()
    return opts


class LastIP(object):
    def __init__(self):
        self.fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lastip")
    def Read(self):
        try:
            with open(self.fn, "r") as fp:
                return fp.read()
        except:
            return None
    def Write(self, value):
        with open(self.fn, "w") as fp:
            fp.write(value)


class DNSPod(object):
    def __init__(self, login_token, domain_id, record_id):
        self.ip = LastIP().Read()
        self.login_token = login_token
        self.domain_id = domain_id
        self.record_id = record_id

    def run(self):
        ip = self.GetIP()
        if ip and ip != self.ip:
            logger().info("IP changed from '%s' to '%s'", self.ip, ip)
            if self.DDns("h", ip):
                self.ip = ip
                LastIP().Write(self.ip)

    def GetIP(self):
        try:
            sock = socket.create_connection(address = ('ns1.dnspod.net', 6666), timeout = 10)
            ip = sock.recv(32)
            logger().info("GetIP: %s", ip)
            sock.close()
            return ip
        except Exception,e:
            logger().error("GetIP Error: %s", e)
            return None

    def DDns(self, sub_domain, value):
        headers = {
                "User-Agent":"github.com#migege#dnspod/0.0.1 (lzw.whu@gmail.com)",
                }

        data = {
                "login_token":self.login_token,
                "format":"json",
                "domain_id":self.domain_id,
                "record_id":self.record_id,
                "sub_domain":sub_domain,
                "record_line":"默认",
                }

        url = "https://dnsapi.cn/Record.Ddns"
        try:
            r = requests.post(url, data = data, headers = headers)
            print r.json()
            if int(r.json()["status"]["code"]) == 1:
                logger().info("DDns OK")
                return True
            else:
                logger().error("DDns response: %s", r.text)
                return False
        except Exception,e:
            logger().error("DDns Error: %s", e)
            return False


if __name__ == '__main__':
    opts = getopts()
    conf = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), opts.config), "r"))
    dnspod = DNSPod(login_token = conf["token"], domain_id = conf["domain_id"], record_id = conf["record_id"])
    dnspod.run()
