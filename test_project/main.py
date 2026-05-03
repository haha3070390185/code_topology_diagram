"""
主模块 - 程序入口
"""

from module_b import business_logic, DerivedClass
from module_a import utility_function


def main():
    """主函数"""
    print("=== 开始执行主程序 ===")
    
    # 调用业务逻辑
    business_logic()
    
    # 创建派生类实例
    obj = DerivedClass("test_object", 100)
    
    # 调用高级处理
    result = obj.advanced_process()
    print(f"高级处理结果: {result}")
    
    # 直接调用工具函数
    utility_function()
    
    print("=== 程序执行结束 ===")


if __name__ == "__main__":
    main()
