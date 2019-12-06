*** Settings ***
Documentation            Update firmware on a target BMC via Redifsh.

# Test Parameters:
# IMAGE_FILE_PATH        The path to the BMC image file.
#
# Firmware update states:
#     Enabled            Image is installed and either functional or active.
#     Disabled           Image installation failed or ready for activation.
#     Updating           Image installation currently in progress.

Resource                 ../../lib/resource.robot
Resource                 ../../lib/bmc_redfish_resource.robot
Resource                 ../../lib/openbmc_ffdc.robot
Resource                 ../../lib/common_utils.robot
Resource                 ../../lib/code_update_utils.robot
Resource                 ../../lib/dump_utils.robot
Resource                 ../../lib/logging_utils.robot
Resource                 ../../lib/redfish_code_update_utils.robot
Library                  ../../lib/gen_robot_valid.py
Library                  ../../lib/tftp_update_utils.py

Suite Setup              Suite Setup Execution
Suite Teardown           Redfish.Logout
Test Setup               Printn
Test Teardown            FFDC On Test Case Fail

Force Tags               BMC_Code_Update

*** Test Cases ***
Redfish Code Update With ApplyTime OnReset
    [Documentation]  Update the firmaware image with ApplyTime of OnReset.
    [Tags]  Redfish_Code_Update_With_ApplyTime_OnReset
    [Template]  Redfish Update Firmware

    # policy
    OnReset  ${IMAGE0_FILE_PATH}

Redfish Code Update With ApplyTime Immediate
    [Documentation]  Update the firmaware image with ApplyTime of Immediate.
    [Tags]  Redfish_Code_Update_With_ApplyTime_Immediate
    [Template]  Redfish Update Firmware

    # policy
    Immediate  ${IMAGE1_FILE_PATH}

Redfish Code Update With Multiple Firmware
    [Documentation]  Update the firmaware image with ApplyTime of OnReset.
    [Tags]  Redfish_Code_Update_With_Multiple_Firmware
    [Template]  Redfish Multiple Upload Image And Check Progress State

    # policy   image_file_path     alternate_image_file_path
    OnReset  ${IMAGE0_FILE_PATH}  ${IMAGE1_FILE_PATH}


*** Keywords ***

Suite Setup Execution
    [Documentation]  Do the suite setup.

    # Checking for file existence.
    Valid File Path  IMAGE0_FILE_PATH
    Valid File Path  IMAGE1_FILE_PATH

    Redfish.Login
    Delete All BMC Dump
    Redfish Purge Event Log


Redfish Update Firmware
    [Documentation]  Update the BMC firmware via redfish interface.
    [Arguments]  ${apply_time}  ${image_file_path}

    # Description of argument(s):
    # policy     ApplyTime allowed values (e.g. "OnReset", "Immediate").

    ${state}=  Get Pre Reboot State
    Rprint Vars  state

    # Redfish Upload Image And Check Progress State  ${apply_time}  ${image_file_path}
    Set ApplyTime  policy=${apply_Time}
    Redfish Upload Image  /redfish/v1/UpdateService  ${image_file_path}
    Reboot BMC And Verify BMC Image
    ...  ${apply_time}  start_boot_seconds=${state['epoch_seconds']}  image_file_path=${image_file_path}
    Verify Get ApplyTime  ${apply_time}


Redfish Multiple Upload Image And Check Progress State
    [Documentation]  Update multiple BMC firmware via redfish interface and check status.
    [Arguments]  ${apply_time}  ${IMAGE_FILE_PATH}  ${ALTERNATE_IMAGE_FILE_PATH}

    # Description of argument(s):
    # apply_time                 ApplyTime allowed values (e.g. "OnReset", "Immediate").
    # IMAGE_FILE_PATH            The path to BMC image file.
    # ALTERNATE_IMAGE_FILE_PATH  The path to alternate BMC image file.

    Valid File Path  ALTERNATE_IMAGE_FILE_PATH
    ${state}=  Get Pre Reboot State
    Rprint Vars  state

    Set ApplyTime  policy=${apply_time}

    ${image_version}=  Get Version Tar  ${IMAGE_FILE_PATH}
    Rprint Vars  image_version
    Redfish Upload Image  ${REDFISH_BASE_URI}UpdateService  ${IMAGE_FILE_PATH}
    Sleep  30s
    ${image_info}=  Get Software Inventory State By Version  ${image_version}
    ${first_image_id}=  Get Image Id By Image Info  ${image_info}
    Rprint Vars  first_image_id
    Sleep  5s

    ${image_version}=  Get Version Tar  ${ALTERNATE_IMAGE_FILE_PATH}
    Rprint Vars  image_version
    Redfish Upload Image  ${REDFISH_BASE_URI}UpdateService  ${ALTERNATE_IMAGE_FILE_PATH}
    Sleep  30s
    ${image_info}=  Get Software Inventory State By Version  ${image_version}
    ${second_image_id}=  Get Image Id By Image Info  ${image_info}
    Rprint Vars  second_image_id

    #Check Image Update Progress State
    #...  match_state='Updating', 'Disabled'  image_id=${first_image_id}

    #Check Image Update Progress State
    #...  match_state='Updating'  image_id=${second_image_id}

    Wait Until Keyword Succeeds  8 min  20 sec
    ...  Check Image Update Progress State
    ...    match_state='Enabled'  image_id=${second_image_id}

    Reboot BMC And Verify BMC Image
    ...  ${apply_time}  start_boot_seconds=${state['epoch_seconds']}  image_file_path=${ALTERNATE_IMAGE_FILE_PATH}

Get Image Id By Image Info
    [Documentation]  Get image ID from image_info.
    [Arguments]  ${image_info}

    [Return]  ${image_info["image_id"]}
