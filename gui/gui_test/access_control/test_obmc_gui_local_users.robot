*** Settings ***

Documentation  Test OpenBMC GUI "Local user management" sub-menu of "Access control".

Resource        ../../lib/resource.robot

Suite Setup     Launch Browser And Login GUI
Suite Teardown  Close Browser
Test Setup      Test Setup Execution


*** Variables ***
${xpath_local_user_management_heading }  //h1[text()="Local user management"]
${xpath_select_user}                     //input[contains(@class,"custom-control-input")]
${xpath_account_policy}                  //button[contains(text(),'Account policy settings')]
${xpath_add_user}                        //button[contains(text(),'Add user')]
${xpath_edit_user}                       //button[@aria-label="Edit user"]
${xpath_delete_user}                     //button[@aria-label="Delete user"]
${xpath_account_status_enabled_button}   //*[@data-test-id='localUserManagement-radioButton-statusEnabled']
${xpath_account_status_disabled_button}  //*[@data-test-id='localUserManagement-radioButton-statusDisabled']
${xpath_username_input_button}           //*[@data-test-id='localUserManagement-input-username']
${xpath_privilege_list_button}           //*[@data-test-id='localUserManagement-select-privilege']
${xpath_password_input_button}           //*[@data-test-id='localUserManagement-input-password']
${xpath_password_confirm_button}         //*[@data-test-id='localUserManagement-input-passwordConfirmation']
${xpath_cancel_button}                   //*[@data-test-id='localUserManagement-button-cancel']
${xpath_submit_button}                   //*[@data-test-id='localUserManagement-button-submit']
${xpath_add_user_heading}                //h5[contains(text(),'Add user')]
${xpath_policy_settings_header}          //*[text()="Account policy settings"]
${xpath_auto_unlock}                     //*[@data-test-id='localUserManagement-radio-automaticUnlock']
${xpath_manual_unlock}                   //*[@data-test-id='localUserManagement-radio-manualUnlock']
${xpath_max_failed_login}                //*[@data-test-id='localUserManagement-input-lockoutThreshold']

*** Test Cases ***

Verify Navigation To Local User Management Page
    [Documentation]  Verify navigation to local user management page.
    [Tags]  Verify_Navigation_To_Local_User_Management_Page

    Page Should Contain Element  ${xpath_local_user_management_heading}


Verify Existence Of All Sections In Local User Management Page
    [Documentation]  Verify existence of all sections in local user management page.
    [Tags]  Verify_Existence_Of_All_Sections_In_Local_User_Management_Page

    Page should contain  View privilege role descriptions


Verify Existence Of All Input Boxes In Local User Management Page
    [Documentation]  Verify existence of all sections in Manage Power Usage page.
    [Tags]  Verify_Existence_Of_All_Input_Boxes_In_Local_User_Management_Page

    Page Should Contain Checkbox  ${xpath_select_user}


Verify Existence Of All Buttons In Local User Management Page
    [Documentation]  Verify existence of all buttons in local user management page.
    [Tags]  Verify_Existence_Of_All_Buttons_In_Local_User_Management_Page

    Page should contain Button  ${xpath_account_policy}
    Page should contain Button  ${xpath_add_user}
    Page Should Contain Button  ${xpath_edit_user}
    Page Should Contain Button  ${xpath_delete_user}


Verify Existence Of All Button And Fields In Add User
    [Documentation]  Verify existence of all buttons and fields in add user page.
    [Tags]  Verify_Existence_Of_All_Button_And_Fields_In_Add_User

    Click Element  ${xpath_add_user}
    Wait Until Page Contains Element  ${xpath_add_user_heading}
    Page Should Contain Element  ${xpath_account_status_enabled_button}
    Page Should Contain Element  ${xpath_account_status_disabled_button}
    Page Should Contain Element  ${xpath_username_input_button}
    Page Should Contain Element  ${xpath_privilege_list_button}
    Page Should Contain Element  ${xpath_password_input_button}
    Page Should Contain Element  ${xpath_password_confirm_button}
    Page Should Contain Element  ${xpath_cancel_button}
    Page Should Contain Element  ${xpath_submit_button}


Verify Existence Of All Buttons And Fields In Account Policy Settings
    [Documentation]  Verify existence of all buttons and fields in account policy settings page.
    [Tags]  Verify_Existence_Of_All_Buttons_And_Fields_In_Account_Policy_Settings

    Click Element  ${xpath_account_policy}
    Wait Until Page Contains  ${xpath_policy_settings_header}
    Page Should Contain Element  ${xpath_auto_unlock}
    Page Should Contain Element  ${xpath_manual_unlock}
    Page Should Contain Element  ${xpath_max_failed_login}
    Page Should Contain Element  ${xpath_submit_button}
    Page Should Contain Element  ${xpath_cancel_button}

*** Keywords ***

Test Setup Execution
    [Documentation]  Do test case setup tasks.

    # Navigate to https://xx.xx.xx.xx/#/access-control/local-user-management  Local users page.

    Click Element  ${xpath_access_control_menu}
    Click Element  ${xpath_local_user_management_sub_menu}
    Wait Until Keyword Succeeds  30 sec  10 sec  Location Should Contain  local-user-management
