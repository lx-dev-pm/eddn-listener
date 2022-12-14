import logging
import os
from threading import Thread

import click
import structlog as structlog

from .io.database import Database
from .io.file import File
from .orchestrator.eddn_orchestrator import EddnOrchestrator


class EDDNListener:
    _orchestrator: EddnOrchestrator
    _file_tools: File = None
    _parameters: dict
    _init_thread: Thread

    def __init__(self, log_level: str = 'INFO'):
        self._parameters = {}
        database = self.__build_db_from_param()
        self._orchestrator = EddnOrchestrator(database)

        structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(
                        logging.getLevelName(log_level)),
        )
        self._log = structlog.get_logger()

        self._parameters.update({
                'log_level': log_level
        })

    def __build_db_from_param(self):
        db_host = os.getenv("DB_HOST", default="localhost")
        db_port = os.getenv("DB_PORT", default="5432")
        db_user = os.getenv("DB_USER", default="edsm-mirror")
        db_name = os.getenv("DB_NAME", default="edsm-mirror")
        db_password = os.getenv("DB_PASSWORD", default="edsm-mirror")
        database = Database(db_host, db_port, db_user, db_name, db_password)

        self._parameters.update({
                'db_host'    : db_host,
                'db_port'    : db_port,
                'db_user'    : db_user,
                'db_name'    : db_name,
                'db_password': '*************',
        })

        return database

    def run(self):
        self._log.debug(f'===  Starting parameters')
        for key in self._parameters:
            self._log.debug(f'===  {key}: {self._parameters[key]}')

        self._orchestrator.run_listener()


@click.command(no_args_is_help=True)
@click.option('--api_key', help="The EDSM api key")
@click.option('--commander_name', help="The EDSM registered commander name")
@click.option('--init_file_path', help="The file path to the system json file for init")
@click.option('--log_level', help="The log level for trace")
def command_line(api_key: str, commander_name: str, init_file_path: str, log_level: str):
    """Start the eddn listener application

    example:
    eddn-listener --log_level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
    """
    print(f'=== Starting {EDDNListener.__name__} ===')
    eddn_listener = EDDNListener(log_level)
    eddn_listener.run()


if __name__ == '__main__':
    command_line()
