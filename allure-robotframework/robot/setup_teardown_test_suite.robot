*** Settings ***
Documentation    Test for the Robot Framework adapter for Allure reports for a suite with setup and teardown keywords

Suite Setup  Log  Starting Test Suite

Suite Teardown  Log  Finishing Test Suite

Test Setup  Log  Starting Test Case

Test Teardown  Log  Finishing Test Case

*** Test Cases ***
Simple Test Case
  [Documentation]  A simple passing test case as listener demo with setup and teardown keywords
  ${test_var}=  Set Variable  OK
  Should Be Equal  ${test_var}  OK

*** Keywords ***
