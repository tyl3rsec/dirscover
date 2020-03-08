# -*- coding: utf-8 -*-

from argparse import ArgumentParser, FileType, HelpFormatter
from sys import argv, exit, stdout
from requests import get, post, put, delete, head, options, codes, exceptions
from time import sleep, strftime, gmtime

class CapitalisedHelpFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = '\033[1;36m❰\033[1;33m!\033[1;36m❱ \033[1;97mUsage\033[0;0m: '
        return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)

argparse = ArgumentParser(prog="Dirscover", usage="{} <url> <wordlist>.".format(argv[0]),
        description="Tool to enumerate website directories",
        formatter_class=CapitalisedHelpFormatter)
argparse._positionals.title = 'Positional arguments'
argparse._optionals.title = 'Optional arguments'
argparse.add_argument("url", help="Url to fuzz", type=str)
argparse.add_argument("wordlist", help="Wordlist to use", type=FileType('r', encoding='utf-8'))
argparse.add_argument("--params", help="Optional url parameters", type=dict, dest="params")
argparse.add_argument("--method", help="HTTP method", type=str, default="GET", dest="method")
argparse.add_argument("--agent", help="Custom user-agent (fill with \"random\" to randomize)", type=str, default="Dirscover v1.0", dest="agent")
argparse.add_argument("--data", help="POST request data", type=dict, dest="data")
argparse.add_argument("--cookies", help="Request cookies", type=dict, dest="cookies")
args = argparse.parse_args()

HTTP_METHODS = [ 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS' ]

if not args.method in HTTP_METHODS:
    print('\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: invalid method specified (`{}`).'.format(args.method))
    exit(1)

def customAgent(agent):
    if (agent != "random"):
        return { "User-Agent": agent }
    else:
        try:
            with open("/wordlists/user-agent.txt") as wordlist:
                return { "User-Agent": choice(wordlist.readlines()) }
        except:
            print('\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: couldn\'t find user-agent wordlist (`./wordlists/user-agent.txt`).')
            exit(1)

wordlist = args.wordlist.read().split()
index = list()

def printStats(request, directory):
    template = """
     \r «˹=========================( \033[38:5:29mDirscover \033[38:5:15m)=========================˺»
     \r   \033[38:5:6m┌[ \033[38:5:3mRequest data:
     \r   \033[38:5:6m└─┬[ \033[38:5:15mHost: \033[38:5:228m{host}
     \r   \033[38:5:6m  ├[ \033[38:5:15mHTTP method: \033[38:5:228m{method}
     \r   \033[38:5:6m  ├[ \033[38:5:15mUser-agent: \033[38:5:228m{agent}
     \r  \033[38:5:6m   └[ \033[38:5:15mPing: \033[38:5:228m{ping:.1f}\033[38:5:15mms
     \r   \033[38:5:6m┌[ \033[38:5:3mWordlist data:
     \r  \033[38:5:6m └─┬[ \033[38:5:15mFile: \033[38:5:228m{filename}
     \r   \033[38:5:6m  ├[ \033[38:5:15mLoaded: \033[38:5:228m{wc} \033[38:5:15mwords
     \r     \033[38:5:6m└[ \033[38:5:15mEstimated time: \033[38:5:228m{etime}
     \r   \033[38:5:6m┌[ \033[38:5:3mStatus:
     \r \033[38:5:6m  └─┬[ \033[38:5:15mTesting: \033[38:5:228m{testing}
     \r     \033[38:5:6m└[ \033[38:5:15mRemaining: \033[38:5:228m{remaining} \033[38:5:15mwords
     \r
               """.format(host=args.url, method=request.request.method.upper(), agent=request.request.headers['User-Agent'],
                       ping=request.elapsed.total_seconds()*1000, filename=args.wordlist.name, wc=len(wordlist), 
                       etime=strftime("%H:%M:%S", gmtime((int(request.elapsed.total_seconds())) * (len(wordlist) - wordlist.index(directory)))),
                       testing=directory, remaining=len(wordlist) - wordlist.index(directory))
    length = len(template.split('\n')[1:])
    stdout.write('\n'*length)
    stdout.write(u'\033[{}F\033[0J '.format(length))
    for line in template.split('\n')[1:]:
        stdout.write(line)
        stdout.write(u'\033[1E')
    if request.status_code == codes.ok:
        index.append({ 'host':args.url.strip() + path.strip(), 'code':request.status_code })
    for discovered in index:
        stdout.write("\r» {} (Code: {})".format(discovered['host'], discovered['code']))
    stdout.write(u'\033[' + str(length + len(index)) + 'F')
    stdout.flush()

for directory in wordlist:
    path = '{}/{}'.format(args.url, directory)
    try:
        request = eval("{}(path, params=args.params, headers=customAgent(args.agent), data=args.data, cookies=args.cookies)".format(args.method.lower()))
    except (exceptions.InvalidSchema, exceptions.MissingSchema):
        print('\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: invalid url structure (missing schema).'.format(args.url.strip()))
        exit(1)
    except KeyboardInterrupt:
        stdout.write('\033[{}B\r\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: execution interrupted by user (`<CTRL+C>`).\n'.format(14+len(index)))
        exit(1)

    printStats(request, directory)

    if request.status_code == codes.ok:
        print("\t» {} (Code: {})".format(args.url.strip() + path.strip(), request.status_code))
