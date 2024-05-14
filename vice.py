import datetime

class Vice:
    def __init__(self, name):
        self.name = name.capitalize()
        self.status = "Active"
        self.log = [{"action": "created", "timestamp": self.current_time()}]
        self.relapse_count = 0
        self.quit_count = 1

    @classmethod
    def from_dict(cls, data):
        vice = cls(data['name'])
        vice.status = data['status']
        vice.log = data['log']
        vice.relapse_count = data['relapse_count']
        vice.quit_count = data['quit_count']
        return vice

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "log": self.log,
            "relapse_count": self.relapse_count,
            "quit_count": self.quit_count
        }

    def current_time(self):
        return datetime.datetime.utcnow().isoformat()

    def relapse(self):
        self.status = "Inactive"
        self.log.append({"action": "relapsed", "timestamp": self.current_time()})
        self.relapse_count += 1

    def quit(self):
        self.status = "Active"
        self.log.append({"action": "quit", "timestamp": self.current_time()})
        self.quit_count += 1
