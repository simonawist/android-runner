import os
import errno
import logging


class Profiler(object):
    @staticmethod
    def get_dependencies():
        return []

    def __init__(self, basedir, config):
        self.basedir = basedir
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self, device_id):
        self.logger.debug('%s: Loading configuration' % device_id)
        self.logger.info('Loading configuration')

    def start_profiling(self, device_id):
        self.logger.debug('%s: Start profiling' % device_id)
        self.logger.info('Start profiling')

    def stop_profiling(self, device_id):
        self.logger.debug('%s: Stop profilers' % device_id)
        self.logger.info('Stop profilers')

    def collect_results(self, device_id, path=None):
        self.logger.debug('%s: Collecting data' % device_id)
        self.logger.info('Collecting data')

    def unload(self, device_id):
        self.logger.debug('%s: Cleanup' % device_id)
        self.logger.info('Cleanup')


def makedirs(path):
    # https://stackoverflow.com/a/5032238
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
