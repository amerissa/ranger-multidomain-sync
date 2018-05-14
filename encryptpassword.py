#!/usr/bin/env python
import base64

password = raw_input('Password to Encrypt: ')

print(base64.b64encode(password))
