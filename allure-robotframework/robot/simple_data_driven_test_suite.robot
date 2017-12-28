*** Settings ***
Documentation    Simple data driven test suite

Test Template  Data Driven Test Template

*** Variables ***

*** Test Cases ***  Result  ValueA  ValueB
 Values should be equal          Should Be Equal              OK      OK
 Values should not be equal      Should Not Be Equal          OK      NOK
 Integer values should be equal  Should Be Equal As Integers  42      ${42}
 Number values should be equal   Should Be Equal As Numbers   1.2345  ${1.2345}
 String should end with          Should End With              Banana  OK

*** Keywords ***
Data Driven Test Template
    [Arguments]  ${Result}  ${ValueA}  ${ValueB}
    Run Keyword  ${Result}  ${ValueA}  ${ValueB}


