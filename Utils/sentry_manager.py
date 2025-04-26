"""
Sentry崩溃报告管理模块
用于初始化和配置Sentry，收集应用程序崩溃信息
"""

import re
import requests
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


class SentryManager:
    """Sentry管理器，用于初始化和配置Sentry"""

    def __init__(self, config_manager):
        """
        初始化Sentry管理器

        Args:
            config_manager: 配置管理器实例，用于获取和保存配置
        """
        self.config_manager = config_manager
        self.initialized = False

    def initialize(self, dsn1, dsn2, version):
        """
        初始化Sentry

        Args:
            dsn1: 主要的Sentry DSN
            dsn2: 备用的Sentry DSN
            version: 应用程序版本
        """
        try:
            # 获取Sentry DSN选择器
            html_str = requests.get('https://gitee.com/kioley/sentryit').content.decode()
            sentry_dsn_check = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]

            # 根据选择器选择DSN
            dsn = dsn1 if sentry_dsn_check == '1' else dsn2

            # 获取用户身份识别码
            piv_key = self.config_manager.get_config_value('PIV', 'PIV_KEY', '')

            # 设置用户上下文
            user_context = {
                'id': piv_key,
                'version': version
            }

            # 初始化Sentry SDK
            sentry_sdk.init(
                dsn=dsn,
                integrations=[LoggingIntegration()],
                send_default_pii=True,
                ignore_errors=self.get_ignore_error_list(),
            )

            # 设置用户上下文
            with sentry_sdk.configure_scope() as scope:
                scope.set_user(user_context)

            self.initialized = True
            # 不在这里记录日志，避免重复

        except Exception as e:
            logging.error(f"Sentry初始化失败: {str(e)}")

    def get_ignore_error_list(self):
        """
        获取Sentry需要忽略的错误列表

        Returns:
            list: 需要忽略的错误类型列表
        """
        try:
            html_str = requests.get('https://gitee.com/kioley/sentryig').content.decode()
            ignore_error = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
            ignore_error_list = [item.strip() for item in ignore_error.split(',')]
            return ignore_error_list
        except Exception as e:
            logging.error(f"获取Sentry忽略错误列表失败: {str(e)}")
            return []

    def update_user_context(self, piv_key=None, version=None):
        """
        更新用户上下文信息

        Args:
            piv_key: 用户身份识别码
            version: 应用程序版本
        """
        if not self.initialized:
            return

        try:
            with sentry_sdk.configure_scope() as scope:
                user_context = {}

                if piv_key is not None:
                    user_context['id'] = piv_key

                if version is not None:
                    user_context['version'] = version

                if user_context:
                    scope.set_user(user_context)
        except Exception as e:
            logging.error(f"更新Sentry用户上下文失败: {str(e)}")

    def capture_exception(self, exception):
        """
        手动捕获异常并发送到Sentry

        Args:
            exception: 异常对象
        """
        if not self.initialized:
            return

        try:
            sentry_sdk.capture_exception(exception)
        except Exception as e:
            logging.error(f"Sentry捕获异常失败: {str(e)}")
