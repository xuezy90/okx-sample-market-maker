import logging
import os
from logging.handlers import TimedRotatingFileHandler

from okx_market_maker.utils.LogFileEnum import LogFileEnum


class LogUtil:
    def __init__(self, fileName: LogFileEnum):
        # 获取项目根目录
        project_dir = os.path.dirname(os.path.dirname(__file__))
        # 配置日志文件路径
        market_file_path = os.path.join(project_dir, 'logs', 'market-data-service.log')
        order_file_path = os.path.join(project_dir, 'logs', 'order-mng-service.log')
        position_file_path = os.path.join(project_dir, 'logs', 'position-mng-service.log')
        strategy_file_path = os.path.join(project_dir, 'logs', 'strategy-mng-service.log')
        default_file_path = os.path.join(project_dir, 'logs', 'default.log')

        file_path = default_file_path
        if fileName == LogFileEnum.MARKET :
            file_path = market_file_path
        elif fileName == LogFileEnum.ORDER:
            file_path = order_file_path
        elif fileName == LogFileEnum.POSITION:
            file_path = position_file_path
        elif fileName == LogFileEnum.STRATEGY:
            file_path = strategy_file_path

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(file_path)
        self.logger.setLevel(logging.INFO)

        # 检查处理器是否已存在，避免重复添加
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 创建文件处理器，每天生成新日志，保留7天
            file_handler = TimedRotatingFileHandler(file_path, when='D', interval=1, backupCount=7)
            file_handler.setLevel(logging.INFO)

            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # 添加处理器到日志记录器
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
