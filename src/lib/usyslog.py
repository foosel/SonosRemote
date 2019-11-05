"""
This syslog client can send UDP packets to a remote syslog server.

Timestamps are not supported for simplicity.

For more information, see RFC 3164.

The MIT License (MIT)

Copyright (c) 2016 Kai Fricke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import usocket

# Facility constants
F_KERN = const(0)
F_USER = const(1)
F_MAIL = const(2)
F_DAEMON = const(3)
F_AUTH = const(4)
F_SYSLOG = const(5)
F_LPR = const(6)
F_NEWS = const(7)
F_UUCP = const(8)
F_CRON = const(9)
F_AUTHPRIV = const(10)
F_FTP = const(11)
F_NTP = const(12)
F_AUDIT = const(13)
F_ALERT = const(14)
F_CLOCK = const(15)
F_LOCAL0 = const(16)
F_LOCAL1 = const(17)
F_LOCAL2 = const(18)
F_LOCAL3 = const(19)
F_LOCAL4 = const(20)
F_LOCAL5 = const(21)
F_LOCAL6 = const(22)
F_LOCAL7 = const(23)

# Severity constants (Names reasonably shortened)
S_EMERG = const(0)
S_ALERT = const(1)
S_CRIT = const(2)
S_ERR = const(3)
S_WARN = const(4)
S_NOTICE = const(5)
S_INFO = const(6)
S_DEBUG = const(7)

class SyslogClient:
    def __init__(self, facility=F_USER):
        self._facility = facility

    def log(self, severity, msg):
        pass

    def alert(self, msg):
        self.log(S_ALERT, msg)

    def critical(self, msg):
        self.log(S_CRIT, msg)

    def error(self, msg):
        self.log(S_ERR, msg)

    def debug(self, msg):
        self.log(S_DEBUG, msg)

    def info(self, msg):
        self.log(S_INFO, msg)

    def notice(self, msg):
        self.log(S_NOTICE, msg)

    def warning(self, msg):
        self.log(S_WARN, msg)

class UDPClient(SyslogClient):
    def __init__(self, ip='127.0.0.1', port=514, facility=F_USER):
        self._addr = usocket.getaddrinfo(ip, port)[0][4]
        self._sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        super().__init__(facility)

    def log(self, severity, msg):
        data = "<%d>%s" % (severity + (self._facility << 3), msg)
        self._sock.sendto(data.encode(), self._addr)
        
    def close(self):
        self._sock.close()

