from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from colorama import Style
from colorama import Fore
import argparse
import asyncio
import logging
import re

raw_message = []

class out:
    def green(self, msg):
        print(Fore.GREEN + msg + Style.RESET_ALL)

    def blue(self, msg):
        print(Fore.BLUE + msg + Style.RESET_ALL)

    def cyan(self, msg):
        print(Fore.CYAN + msg + Style.RESET_ALL)

    def red(self, msg):
        print(Fore.RED + msg + Style.RESET_ALL)

    def yellow(self, msg):
        print(Fore.YELLOW + msg + Style.RESET_ALL)

    def magenta(self, msg):
        print(Fore.MAGENTA + msg + Style.RESET_ALL)

    def news(self, msg):
        print("\n" + Fore.MAGENTA + "##### " + msg + " #####" + Style.RESET_ALL)

    def alert(self, msg):
        print(Fore.RED + "[!] " + msg + Style.RESET_ALL)

    def info(self, msg):
        print(Fore.BLUE + "[*] " + msg + Style.RESET_ALL)

    def info_separator(self, msg):
        print("\n" + Fore.BLUE + "[*] " + msg + Style.RESET_ALL)

    def success(self, msg):
        print(Fore.GREEN + "[+] " + msg + Style.RESET_ALL)

    def debug(self, msg):
        if debug:
            print(Fore.CYAN + "[DEBUG] " + msg + Style.RESET_ALL)

class CustomLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG and 'DATA readline' in record.getMessage()

class CustomLogFormatter(logging.Formatter):
    def format(self, record):
        global raw_message
        original_message = record.getMessage()
        custom_format = f"{Fore.CYAN}{original_message[17:-1]}{Style.RESET_ALL}"
        raw_message.append(original_message[17:-1])
        return custom_format

class SMTPHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        out.news("NEW MESSAGE")
        if not address.endswith('@' + analysis_domain):
            out.alert(f"Discarding message for {address} since it was not ment for {analysis_domain}")
            return f'550 Only receiving for {analysis_domain}!'

        envelope.rcpt_tos.append(address)
        out.info_separator(f"Handling new message from {envelope.mail_from} to {address}!")
        out.cyan('MAIL FROM: %s' % envelope.mail_from)
        out.cyan('RCPT TO: %s' % envelope.rcpt_tos)
        out.debug(f"IP: {session.peer[0]}, port: {session.peer[1]}")
        out.info_separator("Raw message data:")

        return '250 OK'

    async def handle_DATA(self, server, session, envelope):

        global raw_message

        out.info_separator('Decoded message data:')
        message_data = envelope.content.decode('utf8', errors='replace')
        out.cyan(message_data)
        found_identifiers = re.search(f"{smuggling_identifier}START(.*){smuggling_identifier}END", "\r\n".join(raw_message), re.DOTALL)

        if found_identifiers:
            out.success("Found identifiers!")
            out.yellow(found_identifiers.group(0))
        else:
            out.alert("No identifiers found!")

        raw_message = []

        return '250 Success!'

if __name__ == '__main__':
    out = out()
    logging.basicConfig(format=f"{Fore.YELLOW}%(message)s{Style.RESET_ALL}", level=logging.DEBUG)
    logging_handler = logging.getLogger('mail.log')
    logging_handler.addFilter(CustomLogFilter())
    logging_handler.propagate = False
    custom_formatter = CustomLogFormatter()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(custom_formatter)
    logging_handler.addHandler(console_handler)

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("analysis_domain", help="The analysis domain to use for the server.", nargs=1)
    argument_parser.add_argument("--smuggling-identifier", help="Identifier for highlighting received data.", default="SMUGGLING")
    argument_parser.add_argument("--debug", help="Output debug info.", action="store_true")
    argument_parser.add_argument("-p", "--port", help="The port to use.", type=int, default=25)
    args = argument_parser.parse_args()
    analysis_domain = args.analysis_domain[0]
    smuggling_identifier = args.smuggling_identifier
    debug = args.debug
    port = args.port

    controller = Controller(SMTPHandler(), hostname="0.0.0.0", port=port)
    controller.start()
    out.success("SMTP Smuggling Server started!")

    try:
        while True:
            input()
    except (EOFError, KeyboardInterrupt):
        controller.stop()