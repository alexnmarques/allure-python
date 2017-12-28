*** Settings ***
Documentation    Test for the robot adapter for Allure reports

*** Test Cases ***
Simple Passing Test Case
    ${test_var}=   Set Variable  OK
    Should Be Equal  ${test_var}  OK

Simple Failing Test Case
    ${test_var}=  Set Variable  NOK
    Should Be Equal  ${test_var}  OK

*** Keywords ***
