from src.plugins.memory_system.src.memory_manager import MemoryManager

if __name__ == "__main__":
    memory = MemoryManager()  # 创建MemoryManager实例
    memory.import_oie() # 导入OpenIE数据
    memory.query("哲学？")  # 回答问题