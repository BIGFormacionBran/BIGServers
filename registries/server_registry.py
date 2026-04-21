class ServerRegistry:
    SERVERS = [
        {
            "name": "experto",
            "host": "access798302125.webspace-data.io",
            "user": "u98585681",
            "port": 22,
            "type": "sftp"
        },
        {
            "name": "mediaverso",
            "host": "217.160.32.51",
            "user": "root",
            "port": 22,
            "type": "sftp",
            "fingerprint": "ssh-ed25519 255 tdHzrKQGqpimUZeSBrEzUrGojxBCy1Qbv0BD3JA0UNs"
        },
        {
            "name": "dedicado",
            "host": "access901900349.webspace-data.io",
            "user": "u107504604",
            "port": 22,
            "type": "sftp"
        },
        {
            "name": "retodigital",
            "host": "82.223.83.72",
            "user": "root",
            "port": 22,
            "type": "ssh"
        }
    ]

    @classmethod
    def get_all_names(cls):
        return [s['name'] for s in cls.SERVERS]

    @classmethod
    def get_server(cls, name):
        return next((s for s in cls.SERVERS if s['name'].lower() == name.lower()), None)