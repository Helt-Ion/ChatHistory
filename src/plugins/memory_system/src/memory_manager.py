from .config import PG_NAMESPACE, global_config
from .embedding_store import EmbeddingManager
from .kg_manager import KGManager
from .llm_client import LLMClient
from .mem_active_manager import MemoryActiveManager
from .open_ie import OpenIE, handle_import_openie
from .qa_manager import QAManager
from ..global_logger import logger

class MemoryManager:
    def __init__(self):
        try:
            from ..lib import quick_algo
            print("quick_algo库已加载")
        except ImportError:
            print("未找到quick_algo库，无法使用quick_algo算法")
            print("请安装quick_algo库 - 在lib.quick_algo中，执行命令：python setup.py build_ext --inplace")

        # 1.初始化LLM客户端
        logger.info("创建LLM客户端")
        llm_client_list = dict()
        for key in global_config["llm_providers"]:
            llm_client_list[key] = LLMClient(
                global_config["llm_providers"][key]["base_url"],
                global_config["llm_providers"][key]["api_key"],
            )
            print(llm_client_list[key])

        # 2.初始化Embedding库
        self._embed_manager = EmbeddingManager(
            llm_client_list[global_config["embedding"]["provider"]]
        )
        logger.info("正在从文件加载Embedding库")
        try:
            self._embed_manager.load_from_file()
        except Exception as e:
            logger.error("从文件加载Embedding库时发生错误：{}".format(e))
        logger.info("Embedding库加载完成")
        # 3.初始化KG
        self._kg_manager = KGManager()
        logger.info("正在从文件加载KG")
        try:
            self._kg_manager.load_from_file()
        except Exception as e:
            logger.error("从文件加载KG时发生错误：{}".format(e))
        logger.info("KG加载完成")

        logger.info(f"KG节点数量：{len(self._kg_manager.graph.get_node_list())}")
        logger.info(f"KG边数量：{len(self._kg_manager.graph.get_edge_list())}")

        # 数据比对：Embedding库与KG的段落hash集合
        for pg_hash in self._kg_manager.stored_paragraph_hashes:
            key = PG_NAMESPACE + "-" + pg_hash
            if key not in self._embed_manager.stored_pg_hashes:
                logger.warning(f"KG中存在Embedding库中不存在的段落：{key}")

        # 问答系统（用于知识库）
        self._qa_manager = QAManager(
            self._embed_manager,
            self._kg_manager,
            llm_client_list[global_config["embedding"]["provider"]],
            llm_client_list[global_config["qa"]["llm"]["provider"]],
            llm_client_list[global_config["qa"]["llm"]["provider"]],
        )

        # 记忆激活（用于记忆库）
        self._inspire_manager = MemoryActiveManager(
            self._embed_manager,
            llm_client_list[global_config["embedding"]["provider"]],
        )

    def import_oie(self):
        logger.info("正在导入OpenIE数据文件")
        try:
            openie_data = OpenIE.load()
        except Exception as e:
            logger.error("导入OpenIE数据文件时发生错误：{}".format(e))
            return False
        if handle_import_openie(openie_data, self._embed_manager, self._kg_manager) is False:
            logger.error("处理OpenIE数据时发生错误")
            return False
    
    def query(self, question):
        """处理查询"""
        return self._qa_manager.answer_question(question)