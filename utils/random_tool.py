import math

from enums import distrib_ins
import random
import numpy as np
from enums import char_type_ins
import string


class RandomTool:
    distribution = distrib_ins.NORMAL
    # invalid data percentage default 0 max 100
    invalid_percent = 0
    # see np.random.normal
    loc = 0
    # see np.random.normal
    scale = 1

    def set_distribution(self, distribution):
        self.distribution = distribution

    def set_loc(self, loc):
        self.loc = loc

    def set_scale(self, scale):
        self.scale = scale

    def __init__(self, distribution, loc=0, scale=1):
        self.distribution = distribution

    def random_name(self, length=5, min_len=1, max_len=10, char_type=None):
        if char_type is None:
            char_type = [char_type_ins.LETTER, char_type_ins.CHINESE]
        result = []
        if not length:
            length = self.random_int(min_len, max_len)
        # generate specific length name
        for i in range(length):
            random_type = self.choice(char_type)
            if random_type == char_type_ins.NUMBER:
                result.append(self.choice(list(string.digits)))
                continue
            if random_type == char_type_ins.LETTER:
                result.append(self.choice(list(string.ascii_letters)))
                continue
            if random_type == char_type_ins.CHINESE:
                start = int('0x4e00', 16)
                end = int('0x9fff', 16)
                char = chr(self.random_int(start, end))
                result.append(char)
                continue
            if random_type == char_type_ins.SPECIAL:
                result.append(self.choice(list('~!@#$%^&*()_+}{":?><,./\';[]=-')))
                continue
        return ''.join(result)

    def choice(self, array):
        return array[self.random_index(len(array))]

    def random_int(self, lower, upper):
        return self.random_index(upper - lower + 1) + lower

    def random_index(self, size):
        """
        :param size:
        :return: an integer between 0 and size-1
        """
        if self.distribution == distrib_ins.NORMAL:
            return self.__n(size)
        else:
            return random.randint(0, size - 1)

    def __n(self, size):
        """
        :param size: max result value
        :return: an integer that Normally distributed range [0 , size-1]
        """
        # this random produce numbers that statistic mean 0 max scale*3 min -scale*3 by default
        normal_double = np.random.normal(self.loc, self.scale, None)
        # we must scale above number to range [0,size)
        result = math.floor((normal_double + self.scale * 3) * size / (self.scale * 3 * 2))
        # result = math.floor(mu * normal_double + size / 2)
        if result < 0:
            return 0
        if result > size - 1:
            return size - 1
        return result
