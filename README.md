# SMTP Smuggling Tools  
Tools for finding SMTP smuggling vulnerabilities in receiving/inbound and sending/outbound SMTP servers.
- **SMTP Smuggling Scanner: Scanning receiving/inbound SMTP servers**
- *Coming soon: Testing sending/outbound SMTP servers*
- *Coming soon: Custom client for sending analysis e-mails*
- *Coming soon: Further tools*

More information on SMTP smuggling can be found [here](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/).

# SMTP Smuggling Scanner  
The SMTP Smuggling Scanner (smtp_smuggling_scanner.py) can be used to check receiving/inbound SMTP servers for supported end-of-data sequences and SMTP command pipelining. This works by sending e-mails with fake end-of-data sequences like "\n.\n" and appending a second, smuggled e-mail to YOUR@EMAIL.ADDRESS. Therefore, expect some weird looking e-mails coming from test@TESTDOMAIN (e.g., test@check.smtpsmuggling.com) and in some cases (only if you're vulnerable) e-mails from smuggled@TESTDOMAIN (e.g., smuggled@check.smtpsmuggling.com). A non-smuggled test e-mail may look as follows:  
  
![image](https://github.com/The-Login/SMTP-Smuggling-Tools/assets/84237895/b01399c4-b88b-416f-ab32-4c73b86c7ca2)

  
Now, if you receive an e-mail from **smuggled@TESTDOMAIN**, please refer to the section "I'm vulnerable. What now?".
  
*If this scanner doesn't fulfill your needs, please also check out [Hanno's tool](https://github.com/hannob/smtpsmug).*

## Requirements
I have configured check.smtpsmuggling.com (default sender domain) with a neutral SPF record which allows all IP addresses (v=spf1 ?all) and a non-blocking DMARC record (v=DMARC1; p=none). If this setup doesn't work with your e-mailing infrastructure (e.g., e-mails might get blocked), you must set up your own test domain which fulfills your requirements for receiving e-mails (e.g., SPF, DKIM, valid PTR record, etc.).  
We are already working on a better and simpler solution.  
Furthermore, you can install required python modules via:  
```pip install dnspython colorama```

## Usage  
**Setup check:** Sends a test e-mail to verify that the test setup is working correctly. You should receive an e-mail from setup.check@YOURDOMAIN.  
```python3 smtp_smuggling_scanner.py --setup-check YOUR@EMAIL.ADDRESS```  
To use your own domain, run:  
```python3 smtp_smuggling_scanner.py --setup-check --sender-domain YOURTESTDOMAIN YOUR@EMAIL.ADDRESS```  
  
**Smuggling check:** Tries to exploit non-RFC compliant end-of-data sequences and SMTP command pipelining in one go. If this works, you should receive e-mails from test@TESTDOMAIN and SMUGGLED@TESTDOMAIN, as shown above.  
```python3 smtp_smuggling_scanner.py YOUR@EMAIL.ADDRESS```  
To use your own domain, run:  
```python3 smtp_smuggling_scanner.py  --sender-domain YOURTESTDOMAIN YOUR@EMAIL.ADDRESS```  

**Advanced usage:** There are also some options for advanced usage like TLS, custom ports and debugging, however you hopefully won't need those.

# I'm vulnerable. What now?  
If you are using popular software like Postfix, you can find more information on their website (e.g., [www.postfix.org/smtp-smuggling.html](https://www.postfix.org/smtp-smuggling.html)).  
If you don't find any solutions online, please drop me a message on [Mastodon](https://infosec.exchange/@login) or [*X*](https://twitter.com/timolongin).  

# Feedback  
Please create issues and pull requests or give me direct feedback ([Mastodon](https://infosec.exchange/@login) or [*X*](https://twitter.com/timolongin)) to improve these tools.
