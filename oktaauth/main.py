#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys

from oktaauth import metadata

def print_err(s):
    print(s, file=sys.stderr)

def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))

    arg_parser.add_argument(
        '-s', '--server', type=str, help='Okta server', required=True)
    arg_parser.add_argument(
        '-u', '--username', type=str, help='Username', required=True)
    arg_parser.add_argument(
        '-t', '--apptype', type=str, help='Application type', required=True)
    arg_parser.add_argument(
        '-i', '--appid', type=str, help='Application id', required=True)

    config = arg_parser.parse_args(args=argv[1:])

    print_err(epilog)

    print_err("Server: {0}".format(config.server))
    print_err("Username: {0}".format(config.username))
    print_err("Application type: {0}".format(config.apptype))
    print_err("Application ID: {0}".format(config.appid))

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
