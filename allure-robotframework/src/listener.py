import allure_commons
from allure_commons.utils import now
from allure_commons.utils import md5
from allure_commons.utils import uuid4
from allure_commons.utils import represent
from allure_commons.utils import platform_label
from allure_commons.utils import host_tag, thread_tag
from allure_commons.reporter import AllureReporter
from allure_commons.logger import AllureFileLogger
from allure_commons.model2 import TestStepResult, TestResult, TestBeforeResult, TestAfterResult
from allure_commons.model2 import TestResultContainer, ExecutableItem
from allure_commons.model2 import StatusDetails
from allure_commons.model2 import Parameter
from allure_commons.model2 import Label, Link
from allure_commons.model2 import Status
from allure_commons.types import LabelType, Severity
from allure_pytest.utils import allure_labels, allure_links, pytest_markers
from allure_pytest.utils import allure_full_name, allure_package, allure_name
from allure_pytest.utils import get_status, get_status_details
from allure_pytest.utils import get_outcome_status, get_outcome_status_details

from robot.libraries.BuiltIn import BuiltIn


class AllureListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, outputDir=None):
        self.allure_logger = AllureReporter()
        if outputDir is None:
            outputDir = './allure-log'
        self.fileLogger = AllureFileLogger(outputDir)
        self._cache = ItemCache()
        self._host = host_tag()
        self._thread = thread_tag()
        self._currentTest = None
        allure_commons.plugin_manager.register(self.fileLogger)

    def start_suite(self, name, attributes):
        print '\nSTART SUITE'
        print attributes

        suite_uuid = self._cache.set(attributes['id'])

        if len(attributes['id'].split('-')) > 1:
            # update parent group
            parent = self._cache.get('-'.join(attributes['id'].split('-')[:-1]))
            self.allure_logger.update_group(uuid=parent, children=suite_uuid)

        group = TestResultContainer(uuid=suite_uuid, name=name, description=attributes['doc'],
                                    start=now())
        self.allure_logger.start_group(uuid=suite_uuid, group=group)

    def end_suite(self, name, attributes):
        print '\nEND SUITE'
        print attributes
        suite_uuid = self._cache.pop(attributes['id'])
        self.allure_logger.stop_group(uuid=suite_uuid, stop=now())

    def start_test(self, name, attributes):
        print '\nSTART TEST'
        print attributes

        severitySet = False
        test_uuid = self._cache.set(attributes['id'])

        ancestors = []
        parentId = '-'.join(attributes['id'].split('-')[:-1])
        tmp = attributes['id']
        while parentId != tmp:
            ancestors.insert(0, self.allure_logger.get_item(self._cache.get(parentId)).name)
            tmp = parentId
            parentId = '-'.join(parentId.split('-')[:-1]) if len(parentId.split('-')) > 1 else parentId

        parent = self._cache.get('-'.join(attributes['id'].split('-')[:-1]))
        self.allure_logger.update_group(uuid=parent, children=test_uuid)

        full_name = '.'.join(ancestors) + '#' + name

        test_case = TestResult(uuid=test_uuid, name=name, fullName=full_name, start=now())

        for t in attributes['tags']:
            s = t.split('.')
            if s[0] == 'allure_severity':
                test_case.labels.append(Label(name=LabelType.SEVERITY, value=s[1]))
                severitySet = True
            elif s[0] == 'allure_feature':
                test_case.labels.append(Label(name='feature', value='.'.join(s[1:])))
            else:
                test_case.labels.append(Label(name='tag', value='.'.join(s)))

        if not severitySet:
            test_case.labels.append(Label(name=LabelType.SEVERITY, value=Severity.NORMAL))

        test_case.labels.append(Label(name=LabelType.HOST, value=self._host))
        test_case.labels.append(Label(name=LabelType.THREAD, value=self._thread))
        test_case.labels.append(Label(name=LabelType.FRAMEWORK, value='robot-framework'))
        test_case.labels.append(Label(name=LabelType.LANGUAGE, value=platform_label()))

        test_case.labels.append(Label('package', '.'.join(ancestors)))
        test_case.labels.append(Label('testClass', '.'.join(ancestors)))
        test_case.labels.append(Label('parentSuite', '.'.join(ancestors[:-1])))
        test_case.labels.append(Label('suite', ancestors[-1]))
        test_case.labels.append(Label('story', name))

        test_case.historyId = md5(test_case.fullName)

        self.allure_logger.schedule_test(uuid=test_uuid, test_case=test_case)
        self._currentTest = test_uuid

    def end_test(self, name, attributes):
        print '\nEND TEST'
        print attributes

        test_uuid = self._cache.pop(attributes['id'])
        test_case = self.allure_logger.get_test(test_uuid)
        test_case.status = Status.FAILED if attributes['status'] == 'FAIL' else Status.PASSED
        if attributes['status'] == 'PASS':
            test_case.status = Status.PASSED
        elif attributes['status'] == 'FAIL':
            test_case.status = Status.FAILED
        else:
            attributes['status'] = Status.UNKNOWN

        test_case.statusDetails = StatusDetails(message=attributes['message'])
        test_case.stop = now()

        self._currentTest = None
        self.allure_logger.close_test(test_uuid)

    def start_keyword(self, name, attributes):
        print '\nSTART KEYWORD'
        print attributes

        keyword_uuid = self._cache.set(name)
        kw = TestStepResult(id=keyword_uuid, name=name, description=attributes['doc'], start=now())

        if self._currentTest is None:
            # Must be a suite setup or teardown keyword
            parent = self.allure_logger.get_last_item(TestResultContainer).uuid
            if attributes['type'] == 'Setup':
                self.allure_logger.start_before_fixture(parent_uuid=parent, uuid=keyword_uuid, fixture=kw)
            else:
                if attributes['type'] == 'Teardown':
                    self.allure_logger.start_after_fixture(parent_uuid=parent, uuid=keyword_uuid, fixture=kw)
                else:
                    # must be a keyword inside another keyword
                    parent = self.allure_logger.get_last_item(TestStepResult).id
                    self.allure_logger.start_step(parent, keyword_uuid, kw)
        else:
            self.allure_logger.start_step(self._currentTest, keyword_uuid, kw)

    def end_keyword(self, name, attributes):
        print '\nEND KEYWORD'
        print attributes
        keyword_uuid = self._cache.pop(name)
        self.allure_logger.stop_step(uuid=keyword_uuid,id=None,
                                     status=Status.FAILED if attributes['status'] == 'FAIL' else Status.PASSED,
                                     stage='finished' if attributes['status'] == 'PASS' else 'interrupted',
                                     stop=now())

    def log_message(self, message):
        print '\nLOG MESSAGE'
        print message

    def message(self, message):
        pass

    def library_imports(self, name, attributes):
        pass

    def variables_import(self, name, attributes):
        pass

    def close(self):
        print '\nEND EXECUTION'

    @allure_commons.hookimpl
    def attach_data(self, body, name, attachment_type, extension):
        self.allure_logger.attach_data(uuid4(), body, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def attach_file(self, source, name, attachment_type, extension):
        self.allure_logger.attach_file(uuid4(), source, name=name, attachment_type=attachment_type, extension=extension)

    @allure_commons.hookimpl
    def add_link(self, url, link_type, name):
        test_result = self.allure_logger.get_test(None)
        if test_result:
            test_result.links.append(Link(link_type, url, name))

    @allure_commons.hookimpl
    def add_label(self, label_type, labels):
        test_result = self.allure_logger.get_test(None)
        for label in labels if test_result else ():
            test_result.labels.append(Label(label_type, label))


class ItemCache(object):

    def __init__(self):
        self._items = dict()

    def get(self, _id):
        return self._items.get(str(_id))

    def set(self, _id):
        return self._items.setdefault(str(_id), uuid4())

    def pop(self, _id):
        return self._items.pop(str(_id))
