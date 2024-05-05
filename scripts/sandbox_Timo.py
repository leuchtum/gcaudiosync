import numpy as np

class TestClass:
    test_bool: bool = True


test = TestClass()

new_bool = test.test_bool

new_bool = False
print(test.test_bool)