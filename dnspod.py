#!/usr/bin/env python
# -*- coding:utf8 -*-
import os, sys
import requests
import socket
import yaml

reload(sys)
sys.setdefaultencoding("utf8")


def logger():
    import logging
    LOG_FORMAT = "[%(asctime)s]\t[%(levelname)s]\t[%(message)s]"
    LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.txt")
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG, filename=LOG_FILE)
    return logging.getLogger(__name__)


def getopts():
    import argparse
    parser = argparse.ArgumentParser(description='github.com/migege/dnspod')
    parser.add_argument('config', help='config file in yaml')
    opts = parser.parse_args()
    return opts


class Last(object):

    def __init__(self, tag):
        self.fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), tag)

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

    def __init__(self, conf):
        self.ip = Last('last.ip').Read()
        self.conf_md5 = Last('conf.md5').Read()
        self.conf = conf

    def run(self):
        ip = self.GetIP()
        conf_md5 = self.GetConfMD5()
        if ip and ip != self.ip:
            logger().info("IP changed from '%s' to '%s'", self.ip, ip)
            if self.DDns(ip):
                self.ip = ip
                Last('last.ip').Write(self.ip)
                return
        if conf_md5 and conf_md5 != self.conf_md5:
            logger().info("MD5 of conf changed")
            if self.DDns(ip):
                self.ip = ip
                self.conf_md5 = conf_md5
                Last('last.ip').Write(self.ip)
                Last('conf.md5').Write(self.conf_md5)
                return

    def GetIP(self):
        try:
            sock = socket.create_connection(address=('ns1.dnspod.net', 6666), timeout=10)
            ip = sock.recv(32)
            sock.close()
            return ip
        except Exception, e:
            logger().error("GetIP Error: %s", e)
            return None

    def GetConfMD5(self):
        try:
            import hashlib
            import json
            md5 = hashlib.md5(json.dumps(self.conf)).hexdigest()
            return md5
        except Exception, e:
            logger().error('GetConfMD5 Error: %s', e)
            return None

    def __DDnsImpl(self, ip, todo_list):
        url = "https://dnsapi.cn/Record.Ddns"
        headers = {
            "User-Agent": "github.com#migege#dnspod/0.0.2 (lzw.whu@gmail.com)",
        }

        retry_list = []
        for sub_domain, v in todo_list:
            try:
                valid = v["valid"]
                if not valid:
                    continue
            except:
                pass

            try:
                domain_id = v["domain_id"]
                record_id = v["record_id"]
                data = {
                    "login_token": self.conf["token"],
                    "format": "json",
                    "domain_id": domain_id,
                    "record_id": record_id,
                    "sub_domain": sub_domain,
                    "record_line": "默认",
                    "value": ip,
                }

                r = requests.post(url, data=data, headers=headers)
                if int(r.json()["status"]["code"]) == 1:
                    logger().info("DDns OK for subdomain [%s]", sub_domain)
                else:
                    logger().error("DDns response for subdomain [%s]: %s", sub_domain, r.text)
                    retry_list.append((sub_domain, v))
            except Exception, e:
                logger().error("DDns Error for subdomain [%s]: %s", sub_domain, e)
                retry_list.append((sub_domain, v))
        return retry_list

    def DDns(self, ip):
        RETRY_LIMIT = 2
        retry_list = self.__DDnsImpl(ip, self.conf["sub_domains"].items())
        retry = 0
        while retry_list and retry < RETRY_LIMIT:
            retry_list = self.__DDnsImpl(ip, retry_list)
            retry += 1

        if not retry_list:
            return True
        else:
            return False


if __name__ == '__main__':
    opts = getopts()
    conf = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), opts.config), "r"))
    dnspod = DNSPod(conf)
    dnspod.run()
