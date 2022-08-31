#!/usr/bin/env python3

from ast import parse
from bs4 import BeautifulSoup
import email

def email_to_dict(mail):
    return {
        k.capitalize(): str(email.header.make_header(email.header.decode_header(s)))
        for k,s in mail.items()
    }

def file_to_dict(fname):
    sub = fname.split('-', 1)[0]
    with open(fname, 'r') as f:
        parsed = email.message_from_file(f)
        result = { "File": fname[len("/home/cedric/email/"):], "To": parsed["To"] }

        if "From" in parsed:
            result["From"] = parsed["From"]

        if "Subject" in parsed:
            result["Subject"] = parsed["Subject"]

        if "Date" in parsed:
            result["Date"] = parsed["Date"]

        if "Cc" in parsed:
            result["Cc"] = parsed["Cc"]

        if parsed.is_multipart():
            body = "not found"
            for part in parsed.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                charsets = part.get_charsets()

                charset = "utf-8"
                for lookup in charsets:
                    if lookup != None:
                        charset = lookup

                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True).decode(charset)  # decode
                    break

                if ctype == 'text/html' and 'attachment' not in cdispo:
                    html = part.get_payload(decode=True).decode(charset)
                    soup = BeautifulSoup(html, features="lxml")
                    paragraphs = soup.find_all('p')
                    body = ""
                    for paragraph in paragraphs:
                        if paragraph.string != None:
                            body = body + paragraph.string + "\n"
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = parsed.get_payload(decode=True).decode("utf-8")

        result["Body"] = body

        return result

def print_line(headers, l):
    for h in headers:
        s = l.get(h, "")
        print('"' + s.replace('"', '""').replace('\n', ' ') + '"', end=',')
    print("")

def files_to_csv(fnames):
    headers = dict()
    d = []
    for fname in fnames:
        vals = file_to_dict(fname)
        for header in vals.keys(): headers[header] = header
        d.append(vals)
    sortedHeaders = sorted(headers, key=headers.get, reverse=True)
    print_line(sortedHeaders, headers)
    for mail in d:
        print_line(sortedHeaders, mail)

if __name__ == '__main__':
    import sys
    files_to_csv(sys.argv[1:])

    
