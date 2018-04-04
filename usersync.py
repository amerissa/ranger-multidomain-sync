#!/usr/bin/env python2.7

import ldap
import json
import configparser
import logging
import optparse
import sys


class usersync(object):
    def __init__(self, configs):
        self.ldapurl = configs['ldapurl']
        self.basedn = configs['basedn']
        self.username = configs['username']
        self.password = configs['password']
        self.groups = configs['groups'].lower().split(',')
        self.users = []
        self.groupslist = {}
        try:
            logger.info('Connecting to ldap %s', self.ldapurl)
            self.server = ldap.initialize(self.ldapurl)
            logger.info('Connected to ldap %s', self.ldapurl)
        except:
            message = ldap.initialize(self.ldapurl)
            logger.error('Cannot connect to ldap %s' % (self.ldapurl))
            return(None)
        logger.info('Authenticating to ldap %s', self.ldapurl)
        try:
            self.server.simple_bind_s(self.username, self.password)
        except:
            logger.error('Cannot Authenticate to ldap %s' % (self.ldapurl))
            return(None)
        logger.info('Authenticated to ldap %s', self.ldapurl)
        self.groupsandusers()
        logger.debug('List of users %s' % (json.dumps(self.users)))

    def cntosam(self, cn, type):
        attribute = ['sAMAccountName']
        filter = '(&(objectClass=%s)(distinguishedName=%s))' % (type, cn)
        result, configs = self.server.search_s(self.basedn, ldap.SCOPE_SUBTREE, filter, attribute)
        dn, value = result
        sam = value['sAMAccountName'][0]
        logger.debug('sAMAccountName for %s is %s' % (cn, sam))
        return(sam)

    def samtocn(self, sam, type):
        attribute = ['distinguishedName']
        filter = '(&(objectClass=%s)(sAMAccountName=%s))' % (type, sam)
        result, configs = self.server.search_s(self.basedn, ldap.SCOPE_SUBTREE, filter, attribute)
        dn, value = result
        cn = value['distinguishedName'][0]
        logger.debug('CN for %s is %s' % (sam, cn))
        return(cn)

    def groupsandusers(self):
        logger.debug('Creating groups and users dictionary')
        for group in self.groups:
            result = self.server.search_s(self.basedn, ldap.SCOPE_SUBTREE, '(&(objectClass=user)(memberof=%s))' % (self.samtocn(group, 'group')), ['sAMAccountName'])
            users = [b['sAMAccountName'][0] for a, b in result if a is not None]
            self.groupslist.update({group: users})
            for user in users:
                if user not in self.users:
                    self.users.append(user)
                else:
                    continue

    def results(self):
        logger.debug('Creating results list')
        data = {}
        for user in self.users:
            data.update({user: []})
            for group in self.groups:
                if user in self.groupslist[group]:
                    data[user].append(group)
                else:
                    continue
        return(data)

    def close(self):
        logger.info('Disconnecting from ldap %s', self.ldapurl)
        self.server.unbind()


def getkey(item):
    return(item['priority'])


def main():
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    parser.add_option("-c", "--config-file", dest="configs", default="./configs.json", help="Configs file to read from. Must follow json format")
    parser.add_option("-l", "--log-file", dest="logfile", default="./usersync.log", help="Log file location")
    parser.add_option("-o", "--output-file", dest="outputfile", default="./UserGroupSyncFile.json", help="Output file location")
    parser.add_option("-d", "--debug", dest="debug", action="count", help="Debugging logs")
    (options, args) = parser.parse_args()
    configs = options.configs
    logfile = options.logfile
    outputfile = options.outputfile
    debug = options.debug
    global logger
    logger = logging.getLogger('usersync')
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if debug >= 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    try:
        definitions = json.loads(open(configs).read())
    except:
        logger.ERROR("Cannot read configs file %s" % (configs))
        print("Cannot read configs file %s" % (configs))
        sys.exit(1)
    finalresults = {}
    domains = sorted(definitions['domains'], key=getkey)
    for domain in domains:
        logger.info('Starting Sync for domain %s' % (domain['name']))
        setup = usersync(domain)
        users = setup.results()
        if not finalresults:
            finalresults.update(users)
        else:
            keys = set(users.keys()) - set(finalresults.keys())
            duplicates = set(users.keys()) & set(finalresults.keys())
            logger.debug('List of users that are duplicates and not going to sync: %s' % (json.dumps(list(duplicates))))
            for user in list(keys):
                finalresults.update({user: users[user]})
        setup.close()
        logger.info('Ended Sync for domain %s' % (domain['name']))
    output = open(outputfile, 'w')
    output.write(json.dumps(finalresults, indent=4, sort_keys=True))
    output.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nAborting ... Keyboard Interrupt.")
        sys.exit(1)
