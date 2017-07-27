#!/usr/bin/python3

from ctf_gameserver.checker import BaseChecker
from ctf_gameserver.checker.constants import OK, NOTWORKING, NOTFOUND, TIMEOUT
from edn_format import Keyword
import edn_format
from socket import socket, AF_INET, SOCK_STREAM
import random


class DoedelChecker(BaseChecker):
    _ADJECTIVES = ["Hot", "Sexy", "Horny", "Wet", "Gay",
                   "Saucy", "Foxy", "Handsome"]
    _NOUNS = ["Girl", "Woman", "Mama", "Babe", "Gurl", "Darling"]
    _PORT_STATUS = 1667
    _PORT_REQ = 1666
    _MAX_USERS = 20

    def __init__(self, tick, team, service, ip):
        BaseChecker.__init__(self, tick, team, service, ip)

        users_blob_name = "users_" + str(self._team)
        try:
            ub = self.retrieve_yaml(users_blob_name)
            if ub is None:
                self.logger.info("users_blob was None")
                self.store_yaml(users_blob_name, [])
        except:
            self.logger.info("couldn't get users_blob")
            self.store_yaml(users_blob_name, [])

    def generate_user_id(self):
        adj = random.choice(self._ADJECTIVES)
        noun = random.choice(self._NOUNS)
        age = random.randrange(18, 50)
        bruteforce_protection = random.SystemRandom().randrange(0, 1000000)

        return "AAAAaaaa" + adj + noun + str(age) + "-" + str(bruteforce_protection) + "-" + str(self.tick)

    def register_user(self):
        user_id = self.generate_user_id()
        flag = self.get_flag(self.tick)

        self.logger.info("registering user %s", user_id)

        # store users
        users_blob, users_blob_name = self.get_users_blob()
        self.logger.info("old users: %s", users_blob)
        users_blob.append(user_id)
        self.store_yaml(users_blob_name, users_blob)

        self.logger.info("new users %s", users_blob)

        return {"request-type": Keyword("register-user"),
                "user-id": user_id, "security-token": flag}

    def get_patterns(self, user_id, tick):
        request = {"request-type": Keyword("get-patterns"),
                   "user-id": user_id}
        response = self.send_stuff(self._PORT_REQ, request)
        patterns = response[Keyword("patterns")]

        self.logger.info("patterns for %s are %s", str(user_id), str(patterns))

        # store patterns
        self.store_yaml(user_id, patterns)

        return self.check_data(response[Keyword("security-token")], tick)

    def send_data(self, user_id, tick):
        result = []
        patterns = self.retrieve_yaml(user_id)
        for pattern in patterns:
            request = {"request-type": Keyword("send-data"),
                       "user-id": user_id, "pattern": pattern,
                       "excitement-level": random.random()}
            response = self.send_stuff(self._PORT_REQ, request)
            result.append(self.check_data(response[Keyword("security-token")], tick))

        return result

    def get_status(self):
        return {"request-type": Keyword("status")}

    def check_success(self, response):
        try:
            return response[Keyword("response-type")] == Keyword("success")
        except:
            return False

    def check_data(self, flag, tick):
        try:
            if self.get_flag(tick) == flag:
                return True
            else:
                return False
        except:
            return False

    def get_best_pattern(self, user_id, tick):
        response = self.send_stuff(
            self._PORT_REQ, {"request-type": Keyword("get-best-pattern"),
                             "user-id": user_id})
        pattern_string = isinstance(response[Keyword("pattern")], str)
        type_correct = (response[Keyword("response-type")] == Keyword("vibrate"))
        if (not pattern_string) or (not type_correct):
            raise Exception
        return self.check_data(response[Keyword("security-token")], tick)

    def place_flag(self):
        try:
            response = self.send_stuff(self._PORT_REQ, self.register_user())
            self.logger.info("added user")

            if self.check_success(response):
                return OK
            else:
                self.logger.exception("placing flag failed 2")
                return NOTWORKING
        except OSError:
            return TIMEOUT
        except:
            self.logger.exception("placing flag failed")
            return NOTWORKING

    def check_status(self, response):
        return response[Keyword("response-type")] == Keyword("status")

    def check_service(self):
        try:
            # Check status socket.
            if not self.check_status(self.send_stuff(self._PORT_STATUS,
                                                     self.get_status())):
                return NOTWORKING

            return OK
        except OSError:
            return TIMEOUT
        except:
            return NOTWORKING

    def check_flag(self, tick):
        self.logger.info("checking tick %d", tick)

        users_blob, users_blob_name = self.get_users_blob()
        self.logger.info("Users: %s", str(users_blob))

        # Send :get-patterns
        for user_id in users_blob:
            if not user_id.endswith(str(tick)):
                continue
            try:
                self.logger.info("sending for user")
                self.logger.info(str(user_id))
                self.logger.info("Getting Patterns")
                patterns_match = self.get_patterns(user_id, tick)
                self.logger.info("Sending Data")
                send_match = any(self.send_data(user_id, tick))
                self.logger.info("Getting Best Match")
                best_match = self.get_best_pattern(user_id, tick)
                if patterns_match or send_match or best_match:
                    try:
                        pass
                        # users_blob.remove(user_id)
                        # self.store_blob(users_blob_name, pickle.dumps(
                        #     users_blob))
                    except:
                        pass
                    self.expire()
                    return OK
            except OSError:
                return TIMEOUT
            except:
                self.logger.exception("Problems for user %s", str(user_id))
                pass

        self.expire()
        return NOTFOUND

    def expire(self):
        self.logger.info("Expiring Users")
        users_blob, users_blob_name = self.get_users_blob()
        while len(users_blob) > self._MAX_USERS:
            users_blob.pop(0)
        self.store_yaml(users_blob_name, users_blob)

    def get_users_blob(self):
        users_blob_name = "users_" + str(self._team)
        users_blob = self.retrieve_yaml(users_blob_name)
        return users_blob, users_blob_name

    def send_stuff(self, port, painload):
        self.logger.info("Sending %s", str(painload))
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self._ip, port))
        sock.sendall(edn_format.dumps(
            {Keyword(k): v for k, v in painload.items()}).encode('utf8'))
        response = sock.recv(65535)
        self.logger.info('begin response')
        self.logger.info(response.decode('utf8'))
        self.logger.info('end response')
        val = edn_format.loads(response.decode('utf8') + " ")
        sock.close()
        return val
