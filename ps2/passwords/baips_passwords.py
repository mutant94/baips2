from random import randint

from functools import reduce

from ps2.models import UserPasswords


def generate_user_passwords_entities(password):
    masks = []
    ups = []
    x = 0
    while x != 10:
        p_size = randint(5, len(password) - 1)
        up = UserPasswords()
        tmp_psw = set()
        while len(tmp_psw) != p_size:
            tmp_psw.add(randint(0, len(password) - 1))
        tmp_mask = reduce(lambda x, y: x + y, map(lambda x: (2 ** x), tmp_psw))
        if tmp_mask not in masks:
            masks.append(tmp_mask)
            x += 1
        else:
            continue
        up.mask = tmp_mask
        up.set_password("".join(map(lambda x: password[x], tmp_psw)))
        ups.append(up)
    return ups
