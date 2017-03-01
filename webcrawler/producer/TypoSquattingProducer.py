from typo_squat_utils import *
from Producer import Producer
from TaskObject import TaskObject
from .utils import *


class TypoSquattingProducer(Producer):

    def __init__(self, args):
        super(TypoSquattingProducer, self).__init__('TypoSquattingProducer')
        self.args = args

    def get_list_url(self, num_of_url=None):

        assert num_of_url is not None and num_of_url > 0, "num of urls cannot be zero"
        return get_url_list(num_of_url)

    def get_object(self, url):
        return TaskObject("TypoSquattingProducer",
                           url,
                           "selenium_chrome",
                          set_data_requirement(self.args),
                          set_proxy(self.args),
                          set_db(self.args))
