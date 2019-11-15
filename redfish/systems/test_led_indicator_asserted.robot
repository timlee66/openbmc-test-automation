*** Settings ***
Documentation       Check the indicator LEDs on the system can set the assert
...                 property to the correct state.

Resource            ../../lib/rest_client.robot
Resource            ../../lib/bmc_redfish_resource.robot
Resource            ../../lib/bmc_redfish_utils.robot
Resource            ../../lib/openbmc_ffdc.robot
Resource            ../../lib/resource.robot
Resource            ../../lib/boot_utils.robot
Library             ../../lib/gen_robot_valid.py
Library             ../../lib/gen_robot_keyword.py

Suite Setup         Suite Setup Execution
Suite Teardown      Suite Teardown Execution
Test Setup          Printn
Test Teardown       Test Teardown Execution


*** Test Cases ***

Verify Identify Asserted At Standby
    [Documentation]  Verify the LED asserted at standby is set to off or blinking.
    [Tags]  Verify_LED_Identify_Asserted_At_Standby
    [Template]  Set and Verify Identify Indicator

    # pre_req_state     asserted     expected_indicator_led
    Off                 1            Blinking
    Off                 0            Off


Verify Identify Asserted At Runtime
    [Documentation]  Verify the LED asserted at runtime is set to off or blinking.
    [Tags]  Verify_LEDIdentify_Asserted_At_Runtime
    [Template]  Set and Verify Identify Indicator

    # pre_req_state     asserted     expected_indicator_led
    On                  1            Blinking
    On                  0            Off


Verify LED BMC Heartbeat Asserted At Standby
    [Documentation]  Verify the BMC Heartbeat are asserted at standby to lit or off.
    [Tags]  Verify_LED_BMC_Heartbeat_Asserted_At_Standby
    [Template]  Set and Verify LED BMC Heartbeat

    # pre_req_state     asserted                                        expected_indicator_led
    Off                 "xyz.openbmc_project.Led.Physical.Action.Blink"   Blinking
    Off                 "xyz.openbmc_project.Led.Physical.Action.Off"   Off


Verify LED BMC Heartbea Units Asserted At Runtime
    [Documentation]  Verify the BMC Heartbeat are asserted at runtime to lit or off.
    [Tags]  Verify_LED_BMC_Heartbeat_Asserted_At_Runtime
    [Template]  Set and Verify LED BMC Heartbeat

    # pre_req_state     asserted                                        expected_indicator_led
    On                  "xyz.openbmc_project.Led.Physical.Action.Blink"   Blinking
    On                  "xyz.openbmc_project.Led.Physical.Action.Off"   Off

*** Keywords ***

Set and Verify Identify Indicator
    [Documentation]  Verify the indicator LED for the group identify is asserted.
    [Arguments]  ${pre_req_state}  ${asserted}  ${expected_indicator_led}

    # Description of Arguments(s):
    # pre_req_state           The pre-requisite state of the host to perform the test (e.g. "On")
    # asserted                The assert property that sets the value to 0 - Off or 1 - Blinking (e.g. "1")
    # expected_indicator_led  The expected value of the IndicatorLED attribute for all the
    #                         LEDs after the lamp test is initiated (e.g. "Blinking")

    Run Key U  Redfish Power ${pre_req_state} \ stack_mode=skip \ quiet=1
    Redfish.Login
    Redfish.Put  ${LED_IDENTIFY_TEST_ASSERTED_URI}attr/Asserted  body={"data":${asserted}}
    Verify Identify LEDs  ${expected_indicator_led}


Set and Verify LED BMC Heartbeat
    [Documentation]  Verify the indicator LED for the BMC Heartbeat units are asserted.
    [Arguments]  ${pre_req_state}  ${asserted}  ${expected_indicator_led}

    # Description of Arguments(s):
    # pre_req_state           The pre-requisite state of the host to perform the test (e.g. "On")
    # asserted                The assert property that sets the value (e.g. "xyz.openbmc_project.Led.Physical.Action.On")
    # expected_indicator_led  The expected value of the IndicatorLED attribute for all the

    Run Key U  Redfish Power ${pre_req_state} \ stack_mode=skip \ quiet=1
    Redfish.Login
    Redfish.Put  ${LED_PHYSICAL_BMC_URI}attr/State  body={"data":${asserted}}

    Verify Heartbeat LEDs  ${expected_indicator_led}


Verify Identify LEDs
    [Documentation]  Verify the LEDs on the BMC Heartbeat units are set according to caller's expectation.
    [Arguments]  ${expected_indicator_led}

    # Description of Arguments(s):
    # expected_indicator_led  The expected value of the IndicatorLED attribute for all the
    #                         LEDs after the lamp test is initiated (e.g. "Blinking")
    ${resp}=  Redfish.Get  /redfish/v1/Systems/system
    Should Be Equal As Strings  ${resp.dict["IndicatorLED"]}
    ...  ${expected_indicator_led}

Verify Heartbeat LEDs
    [Documentation]  Verify the LEDs on the BMC Heartbeat units are set according to caller's expectation.
    [Arguments]  ${expected_indicator_led}

    # Description of Arguments(s):
    # expected_indicator_led  The expected value of the IndicatorLED attribute for all the
    #                         LEDs after the lamp test is initiated (e.g. "Blinking")
    ${resp}=  Redfish.Get  /redfish/v1/Chassis/bmc
    Should Be Equal As Strings  ${resp.dict["IndicatorLED"]}
    ...  ${expected_indicator_led}


Suite Teardown Execution
    [Documentation]  Do the post suite teardown.

    Redfish.Logout


Suite Setup Execution
    [Documentation]  Do test case setup tasks.

    Printn
    Redfish.Login


Test Teardown Execution
    [Documentation]  Do the post test teardown.

    FFDC On Test Case Fail
