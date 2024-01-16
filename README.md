# SMTP Smuggling Tools  
Tools for finding SMTP smuggling vulnerabilities in inbound/receiving and outbound/sending SMTP servers.
- **SMTP Smuggling Scanner: Scanning inbound and outbound SMTP servers**
- *SMTP Analysis Server: Receive and analyse SMTP traffic (coming soon)*
- *Coming soon: Further tools*

More information on SMTP smuggling can be found [here](https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/).

# SMTP Smuggling Scanner  
This tool can be used to scan for SMTP smuggling vulnerabilities in inbound and outbound SMTP servers.  

*If this scanner doesn't fulfill your needs, please also check out [Hanno's tool](https://github.com/hannob/smtpsmug).*


## Avoiding false positives
**What are we actually looking for?**  
Essentially, the SMTP Smuggling Scanner allows you to find **end-of-data sequences** which outbound SMTP server implementations ignore, but inbound SMTP server implementations accept.  
For example, Exchange Online allowed to pass &lt;LF&gt;.&lt;CR&gt;&lt;LF&gt; sequences **unfiltered** in outbound/sent e-mails. Now, if we're sending an e-mail from Exchange Online with such a &lt;LF&gt;.&lt;CR&gt;&lt;LF&gt; sequence to an inbound/receiving server, it may interpret this sequence as an end-of-data sequence. This was the case for Postfix, Sendmail, Cisco Secure Email and probably other servers. Hence, SMTP smuggling worked from Exchange Online to Postfix, Sendmail and more.  
Therefore, when looking for SMTP smuggling vulnerabilities, we must always look at both sides, outbound and inbound.  

***"I just want to see if someone can send me spoofed e-mails via SMTP smuggling?"***  
In that case, go ahead to "Scanning inbound SMTP servers".

## Requirements
```pip install dnspython colorama```

## Scanning inbound SMTP servers  
The SMTP Smuggling Scanner (smtp_smuggling_scanner.py) can be used to check inbound/receiving SMTP servers for supported end-of-data sequences and SMTP command pipelining. This works by sending e-mails with fake end-of-data sequences like "\n.\n" and appending a second, smuggled e-mail to YOUR@EMAIL.ADDRESS. Therefore, expect some weird looking e-mails coming from test@TESTDOMAIN (e.g., test@check.smtpsmuggling.com) and in some cases (only if you're vulnerable) e-mails from smuggled@TESTDOMAIN (e.g., smuggled@check.smtpsmuggling.com). A non-smuggled test e-mail may look as follows:  
  
![image](https://github.com/The-Login/SMTP-Smuggling-Tools/assets/84237895/b01399c4-b88b-416f-ab32-4c73b86c7ca2)

  
Now, if you receive an e-mail from **smuggled@TESTDOMAIN**, please refer to the section "I'm vulnerable. What now?".

### Inbound scanning requirements
I have configured check.smtpsmuggling.com (default sender domain) with a neutral SPF record which allows all IP addresses (v=spf1 ?all) and a non-blocking DMARC record (v=DMARC1; p=none). If this setup doesn't work with your e-mailing infrastructure (e.g., e-mails might get blocked), you must set up your own test domain which fulfills your requirements for receiving e-mails (e.g., SPF, DKIM, valid PTR record, etc.).  
We are already working on a better and simpler solution.  

### Usage
**Install dependencies:** For the Script to work correctly, all dependencies defined in the requirements.txt file need to be fullfilled.
To install missing modules, you can run ```pip install -r requirements.txt```

**Setup check:** Sends a test e-mail to verify that the test setup is working correctly. You should receive an e-mail from setup.check@YOURDOMAIN.  
```python3 smtp_smuggling_scanner.py --setup-check YOUR@EMAIL.ADDRESS```  
To use your own domain, run:  
```python3 smtp_smuggling_scanner.py --setup-check --sender-domain YOURTESTDOMAIN YOUR@EMAIL.ADDRESS```  
  
**Smuggling check:** Tries to exploit non-RFC compliant end-of-data sequences and SMTP command pipelining in one go. If this works, you should receive e-mails from test@TESTDOMAIN and SMUGGLED@TESTDOMAIN, as shown above.  
```python3 smtp_smuggling_scanner.py YOUR@EMAIL.ADDRESS```  
To use your own domain, run:  
```python3 smtp_smuggling_scanner.py  --sender-domain YOURTESTDOMAIN YOUR@EMAIL.ADDRESS```  

**Advanced usage:** There are also some options for advanced usage like TLS, custom ports and debugging, however you hopefully won't need those.

## Scanning outbound SMTP servers  
The SMTP Smuggling Scanner can also be used to check outbound/sending SMTP servers for unfiltered end-of-data sequences. See "Usage" for more info.  
*Note: Analysing sequences that get passed through outbound SMTP servers unfiltered works best with an inbound SMTP analysis server. However, this is still a work-in-progress. Stay tuned!*

### Usage  
**Setup check:** Sends a test e-mail to verify that the test setup is working correctly. You should receive an e-mail with the subject "SETUP CHECK".  
```python3 smtp_smuggling_scanner.py YOUR@RECEIVER.ADDRESS --outbound-smtp-server SOMESERVER.SMTP.SERVER --port 587 --starttls --sender-address YOUR@EMAIL.ADRESS --username YOUR@EMAIL.ADRESS --password PASSWORD --setup-check```  
  
**Smuggling check:** Sends e-mails containing "fake" end-of-data sequences (e.g., "\n.\n") through the specified outbound server.  
```python3 smtp_smuggling_scanner.py YOUR@RECEIVER.ADDRESS --outbound-smtp-server SOMESERVER.SMTP.SERVER --port 587 --starttls --sender-address YOUR@EMAIL.ADRESS --username YOUR@EMAIL.ADRESS --password PASSWORD```  

# SMTP Analysis Server
*Coming soon*

# I'm vulnerable. What now?  
If you are using popular software like Postfix, you can find more information on their website (e.g., [www.postfix.org/smtp-smuggling.html](https://www.postfix.org/smtp-smuggling.html)).  
If you don't find any solutions online, please drop me a message on [Mastodon](https://infosec.exchange/@login) or [*X*](https://twitter.com/timolongin).  

# Feedback  
Please create issues and pull requests or give me direct feedback ([Mastodon](https://infosec.exchange/@login) or [*X*](https://twitter.com/timolongin)) to improve these tools.
