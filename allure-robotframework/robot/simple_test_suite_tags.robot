*** Settings ***
Documentation    Test for the robot adapter for Allure reports
Force Tags  allure_feature.Tags behaviour
Default Tags  test without tags

*** Test Cases ***
Simple Passing Test Case
    [Tags]  allure_severity.critical  tag_for_testcase1
    ${test_var}=  Set Variable  OK
    Should Be Equal  ${test_var}  OK

Simple Failing Test Case
    [Tags]  allure_severity.blocker  tag_for_testcase2
    ${test_var}=  Set Variable  NOK
    Should Be Equal  ${test_var}  OK

Another Passing test case
    Log  This testcase should have a tag

*** Keywords ***
