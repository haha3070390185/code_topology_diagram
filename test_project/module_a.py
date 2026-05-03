"""
测试模块A - 基础功能模块
"""

def utility_function():
    """一个通用工具函数"""
    print("这是模块A的工具函数")
    return "result_from_a"


class BaseClass:
    """基础类，提供通用功能"""
    
    def __init__(self, name):
        self.name = name
    
    def get_info(self):
        """获取信息"""
        return f"BaseClass: {self.name}"
    
    def process_data(self, data):
        """处理数据"""
        utility_function()
        return processed_data
