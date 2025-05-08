from utils import random_ins
from enums import char_type_ins as char_type
import numpy as np
from config.logger_config import get_logger
import matplotlib.pyplot as plt
import unittest

logger = get_logger()


class TestRandom(unittest.TestCase):
    def test_init(self):
        arr = []
        for i in range(1000):
            random_int = random_ins.random_int(0, 10)
            arr.append(random_int)
            if random_int not in range(1000):
                print(f'{random_int}this number not in range')
        print(f'max {max(arr)}, min {min(arr)}')

    def test_gauss(self):
        arr = []
        for i in range(1000):
            arr.append(random_ins.random_index(10000))
        print(f'最大值{np.max(arr)}')
        print(f'最小值{np.min(arr)}')
        plt.hist(arr)
        plt.show()

    def test_normal_random(self):
        random_ins.scale = 10
        arr = []
        for i in range(1000):
            random_int = random_ins.random_int(0, 10000)
            arr.append(random_int)
            if random_int not in range(10001):
                print(f'{random_int}this number not in range')
        print(f'max {max(arr)}, min {min(arr)}')

    def test_random_name(self):
        print(random_ins.random_name())
        print(random_ins.random_name(char_type=[char_type.LETTER]))
        print(random_ins.random_name(char_type=[char_type.NUMBER]))
        print(random_ins.random_name(char_type=[char_type.CHINESE]))
