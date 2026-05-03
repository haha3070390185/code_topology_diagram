"""
测试模块B - 业务逻辑模块
"""

from module_a import utility_function, BaseClass


def business_logic():
    """业务逻辑函数"""
    result = utility_function()
    print(f"调用模块A的函数，结果: {result}")
    return "business_result"


class DerivedClass(BaseClass):
    """派生类，继承自BaseClass"""
    
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value
    
    def advanced_process(self):
        """高级处理方法"""
        info = self.get_info()
        business_logic()
        return f"DerivedProcess: {info}, value: {self.value}"
    
    def __str__(self):
        return f"DerivedClass(name={self.name}, value={self.value})"
