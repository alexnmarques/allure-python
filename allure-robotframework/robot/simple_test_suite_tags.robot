*** Settings ***
Documentation    Test for the robot adapter for Allure reports
Force Tags  allure_feature.Tags behaviour

*** Test Cases ***
Simple Passing Test Case
    [Tags]  allure_severity.critical
    ${test_var}=  Set Variable  OK
    Should Be Equal  ${test_var}  OK

Simple Failing Test Case
    [Tags]  allure_severity.blocker
    ${test_var}=  Set Variable  NOK
    Should Be Equal  ${test_var}  OK

*** Keywords ***
