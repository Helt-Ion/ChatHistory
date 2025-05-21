from src.plugins.memory_system.src.memory_manager import MemoryManager
from src.plugins.memory_system.src.info_extraction import pre_process

if __name__ == "__main__":
    memory = MemoryManager()  # 创建MemoryManager实例
    pre_process() # 读取文本生成OpenIE数据
    # memory.import_oie() # 导入OpenIE数据到记忆库
    # memory.query("哲学？")  # 回答问题