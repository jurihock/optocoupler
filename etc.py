import click
import lxi
import time

from urllib.parse import urlparse

class Logger:

    def __init__(self):

        self.topics = {
            'PING':    click.style(' PING ',    bg='yellow', fg='black'),
            'ERROR':   click.style(' ERROR ',   bg='red',    fg='white'),
            'SETTING': click.style(' SETTING ', bg='blue',   fg='white'),
            'READING': click.style(' READING ', bg='green',  fg='black'),
        }

    def __call__(self, topic, *args):

        message = ' '.join([str(arg) for arg in args]).strip()
        
        if not message:
            return

        if topic:

            topics = self.topics.keys()
            topic = next((_ for _ in topics if topic.upper() in _.upper()), topic)

            maxwidth = max(len(topic) for topic in topics)
            padwidth = max(maxwidth - len(topic) + 2, 0)

            topics = self.topics
            topic = topics[topic.upper()]

            padding = ' ' * padwidth

            click.echo(topic + padding + message)

        else:

            click.echo(message)

class LxiDevice:

    LxiInit = False

    def __init__(self, url):

        self.url = urlparse(url)
        self.lxi = None

    def __del__(self):

        self.close()

    def sleep(self, timeout):

        time.sleep(timeout)

    def open(self, *, protocol=lxi.protocol.RAW, timeout=1):

        self.close()

        timeout = int(timeout * 1e+3) # ms

        tmp = lxi.connect(self.url.hostname, self.url.port, self.url.username, timeout, protocol)
        assert tmp >= 0, str(tmp)
        self.lxi = tmp

        return self

    def close(self):

        if self.lxi == None:
            return

        lxi.disconnect(self.lxi)
        self.lxi = None

        return self

    def __call__(self, *args, terminator='\r\n', cache=1024, timeout=1):

        timeout = int(timeout * 1e+3) # ms

        command = ' '.join([str(arg) for arg in args]).strip()

        if command:

            command += terminator

            sbytes = lxi.send(self.lxi, command, len(command), timeout)
            assert sbytes == len(command), str(sbytes)

            return None

        else:

            rbytes, message = lxi.receive(self.lxi, cache, timeout)
            assert rbytes >= 0, str(rbytes)

            return message.strip()

    @staticmethod
    def find(name, *, rename=lambda name: name.split('-')[-2].upper(), protocol=lxi.discover_protocol.DISCOVER_MDNS, timeout=1):

        timeout = int(timeout * 1e+3) # ms

        devices = {}

        def service(host, path, scheme, port):
            scheme = str(scheme, 'ascii')
            name = rename(str(path, 'ascii'))
            host = str(host, 'ascii')
            port = int(port)
            path = str(path, 'ascii')
            devices[name] = f'{scheme}://{name}@{host}:{port}/{path}'

        if not LxiDevice.LxiInit:
            lxi.init()
            LxiDevice.LxiInit = True

        info = lxi.lxi_info_class()
        info.service = service

        lxi.discover(info, timeout, protocol)
        assert name in devices, str(devices)

        return LxiDevice(devices[name])
