#!/usr/bin/env python

r"""
This module provides command execution functions such as cmd_fnc and cmd_fnc_u.
"""

import os
import sys
import subprocess
import collections
import signal
import time

import gen_print as gp
import gen_valid as gv
import gen_misc as gm

robot_env = gp.robot_env

if robot_env:
    import gen_robot_print as grp
    from robot.libraries.BuiltIn import BuiltIn


# cmd_fnc and cmd_fnc_u should now be considered deprecated.  shell_cmd and
# t_shell_cmd should be used instead.
def cmd_fnc(cmd_buf,
            quiet=None,
            test_mode=None,
            debug=0,
            print_output=1,
            show_err=1,
            return_stderr=0,
            ignore_err=1):
    r"""
    Run the given command in a shell and return the shell return code and the
    output.

    Description of arguments:
    cmd_buf                         The command string to be run in a shell.
    quiet                           Indicates whether this function should run
                                    the print_issuing() function which prints
                                    "Issuing: <cmd string>" to stdout.
    test_mode                       If test_mode is set, this function will
                                    not actually run the command.  If
                                    print_output is set, it will print
                                    "(test_mode) Issuing: <cmd string>" to
                                    stdout.
    debug                           If debug is set, this function will print
                                    extra debug info.
    print_output                    If this is set, this function will print
                                    the stdout/stderr generated by the shell
                                    command.
    show_err                        If show_err is set, this function will
                                    print a standardized error report if the
                                    shell command returns non-zero.
    return_stderr                   If return_stderr is set, this function
                                    will process the stdout and stderr streams
                                    from the shell command separately.  It
                                    will also return stderr in addition to the
                                    return code and the stdout.
    """

    # Determine default values.
    quiet = int(gm.global_default(quiet, 0))
    test_mode = int(gm.global_default(test_mode, 0))

    if debug:
        gp.print_vars(cmd_buf, quiet, test_mode, debug)

    err_msg = gv.svalid_value(cmd_buf)
    if err_msg != "":
        raise ValueError(err_msg)

    if not quiet:
        gp.pissuing(cmd_buf, test_mode)

    if test_mode:
        if return_stderr:
            return 0, "", ""
        else:
            return 0, ""

    if return_stderr:
        err_buf = ""
        stderr = subprocess.PIPE
    else:
        stderr = subprocess.STDOUT

    sub_proc = subprocess.Popen(cmd_buf,
                                bufsize=1,
                                shell=True,
                                executable='/bin/bash',
                                stdout=subprocess.PIPE,
                                stderr=stderr)
    out_buf = ""
    if return_stderr:
        for line in sub_proc.stderr:
            try:
                err_buf += line
            except TypeError:
                line = line.decode("utf-8")
                err_buf += line
            if not print_output:
                continue
            if robot_env:
                grp.rprint(line)
            else:
                sys.stdout.write(line)
    for line in sub_proc.stdout:
        try:
            out_buf += line
        except TypeError:
            line = line.decode("utf-8")
            out_buf += line
        if not print_output:
            continue
        if robot_env:
            grp.rprint(line)
        else:
            sys.stdout.write(line)
    if print_output and not robot_env:
        sys.stdout.flush()
    sub_proc.communicate()
    shell_rc = sub_proc.returncode
    if shell_rc != 0:
        err_msg = "The prior shell command failed.\n"
        err_msg += gp.sprint_var(shell_rc, 1)
        if not print_output:
            err_msg += "out_buf:\n" + out_buf

        if show_err:
            if robot_env:
                grp.rprint_error_report(err_msg)
            else:
                gp.print_error_report(err_msg)
        if not ignore_err:
            if robot_env:
                BuiltIn().fail(err_msg)
            else:
                raise ValueError(err_msg)

    if return_stderr:
        return shell_rc, out_buf, err_buf
    else:
        return shell_rc, out_buf


def cmd_fnc_u(cmd_buf,
              quiet=None,
              debug=None,
              print_output=1,
              show_err=1,
              return_stderr=0,
              ignore_err=1):
    r"""
    Call cmd_fnc with test_mode=0.  See cmd_fnc (above) for details.

    Note the "u" in "cmd_fnc_u" stands for "unconditional".
    """

    return cmd_fnc(cmd_buf, test_mode=0, quiet=quiet, debug=debug,
                   print_output=print_output, show_err=show_err,
                   return_stderr=return_stderr, ignore_err=ignore_err)


def parse_command_string(command_string):
    r"""
    Parse a bash command-line command string and return the result as a
    dictionary of parms.

    This can be useful for answering questions like "What did the user specify
    as the value for parm x in the command string?".

    This function expects the command string to follow the following posix
    conventions:
    - Short parameters:
      -<parm name><space><arg value>
    - Long parameters:
      --<parm name>=<arg value>

    The first item in the string will be considered to be the command.  All
    values not conforming to the specifications above will be considered
    positional parms.  If there are multiple parms with the same name, they
    will be put into a list (see illustration below where "-v" is specified
    multiple times).

    Description of argument(s):
    command_string                  The complete command string including all
                                    parameters and arguments.

    Sample input:

    robot_cmd_buf:                                    robot -v
    OPENBMC_HOST:dummy1 -v keyword_string:'Set Auto Reboot  no' -v
    lib_file_path:/home/user1/git/openbmc-test-automation/lib/utils.robot -v
    quiet:0 -v test_mode:0 -v debug:0
    --outputdir='/home/user1/status/children/'
    --output=dummy1.Auto_reboot.170802.124544.output.xml
    --log=dummy1.Auto_reboot.170802.124544.log.html
    --report=dummy1.Auto_reboot.170802.124544.report.html
    /home/user1/git/openbmc-test-automation/extended/run_keyword.robot

    Sample output:

    robot_cmd_buf_dict:
      robot_cmd_buf_dict[command]:                    robot
      robot_cmd_buf_dict[v]:
        robot_cmd_buf_dict[v][0]:                     OPENBMC_HOST:dummy1
        robot_cmd_buf_dict[v][1]:                     keyword_string:Set Auto
        Reboot no
        robot_cmd_buf_dict[v][2]:
        lib_file_path:/home/user1/git/openbmc-test-automation/lib/utils.robot
        robot_cmd_buf_dict[v][3]:                     quiet:0
        robot_cmd_buf_dict[v][4]:                     test_mode:0
        robot_cmd_buf_dict[v][5]:                     debug:0
      robot_cmd_buf_dict[outputdir]:
      /home/user1/status/children/
      robot_cmd_buf_dict[output]:
      dummy1.Auto_reboot.170802.124544.output.xml
      robot_cmd_buf_dict[log]:
      dummy1.Auto_reboot.170802.124544.log.html
      robot_cmd_buf_dict[report]:
      dummy1.Auto_reboot.170802.124544.report.html
      robot_cmd_buf_dict[positional]:
      /home/user1/git/openbmc-test-automation/extended/run_keyword.robot
    """

    # We want the parms in the string broken down the way bash would do it,
    # so we'll call upon bash to do that by creating a simple inline bash
    # function.
    bash_func_def = "function parse { for parm in \"${@}\" ; do" +\
        " echo $parm ; done ; }"

    rc, outbuf = cmd_fnc_u(bash_func_def + " ; parse " + command_string,
                           quiet=1, print_output=0)
    command_string_list = outbuf.rstrip("\n").split("\n")

    command_string_dict = collections.OrderedDict()
    ix = 1
    command_string_dict['command'] = command_string_list[0]
    while ix < len(command_string_list):
        if command_string_list[ix].startswith("--"):
            key, value = command_string_list[ix].split("=")
            key = key.lstrip("-")
        elif command_string_list[ix].startswith("-"):
            key = command_string_list[ix].lstrip("-")
            ix += 1
            try:
                value = command_string_list[ix]
            except IndexError:
                value = ""
        else:
            key = 'positional'
            value = command_string_list[ix]
        if key in command_string_dict:
            if isinstance(command_string_dict[key], str):
                command_string_dict[key] = [command_string_dict[key]]
            command_string_dict[key].append(value)
        else:
            command_string_dict[key] = value
        ix += 1

    return command_string_dict


# Save the original SIGALRM handler for later restoration by shell_cmd.
original_sigalrm_handler = signal.getsignal(signal.SIGALRM)


def shell_cmd_timed_out(signal_number,
                        frame):
    r"""
    Handle an alarm signal generated during the shell_cmd function.
    """

    gp.dprint_executing()
    # Get subprocess pid from shell_cmd's call stack.
    sub_proc = gp.get_stack_var('sub_proc', 0)
    pid = sub_proc.pid
    # Terminate the child process.
    os.kill(pid, signal.SIGTERM)
    # Restore the original SIGALRM handler.
    signal.signal(signal.SIGALRM, original_sigalrm_handler)

    return


def shell_cmd(command_string,
              quiet=None,
              print_output=None,
              show_err=1,
              test_mode=0,
              time_out=None,
              max_attempts=1,
              retry_sleep_time=5,
              allowed_shell_rcs=[0],
              ignore_err=None,
              return_stderr=0,
              fork=0):
    r"""
    Run the given command string in a shell and return a tuple consisting of
    the shell return code and the output.

    Description of argument(s):
    command_string                  The command string to be run in a shell
                                    (e.g. "ls /tmp").
    quiet                           If set to 0, this function will print
                                    "Issuing: <cmd string>" to stdout.  When
                                    the quiet argument is set to None, this
                                    function will assign a default value by
                                    searching upward in the stack for the
                                    quiet variable value.  If no such value is
                                    found, quiet is set to 0.
    print_output                    If this is set, this function will print
                                    the stdout/stderr generated by the shell
                                    command to stdout.
    show_err                        If show_err is set, this function will
                                    print a standardized error report if the
                                    shell command fails (i.e. if the shell
                                    command returns a shell_rc that is not in
                                    allowed_shell_rcs).  Note: Error text is
                                    only printed if ALL attempts to run the
                                    command_string fail.  In other words, if
                                    the command execution is ultimately
                                    successful, initial failures are hidden.
    test_mode                       If test_mode is set, this function will
                                    not actually run the command.  If
                                    print_output is also set, this function
                                    will print "(test_mode) Issuing: <cmd
                                    string>" to stdout.  A caller should call
                                    shell_cmd directly if they wish to have
                                    the command string run unconditionally.
                                    They should call the t_shell_cmd wrapper
                                    (defined below) if they wish to run the
                                    command string only if the prevailing
                                    test_mode variable is set to 0.
    time_out                        A time-out value expressed in seconds.  If
                                    the command string has not finished
                                    executing within <time_out> seconds, it
                                    will be halted and counted as an error.
    max_attempts                    The max number of attempts that should be
                                    made to run the command string.
    retry_sleep_time                The number of seconds to sleep between
                                    attempts.
    allowed_shell_rcs               A list of integers indicating which
                                    shell_rc values are not to be considered
                                    errors.
    ignore_err                      Ignore error means that a failure
                                    encountered by running the command string
                                    will not be raised as a python exception.
                                    When the ignore_err argument is set to
                                    None, this function will assign a default
                                    value by searching upward in the stack for
                                    the ignore_err variable value.  If no such
                                    value is found, ignore_err is set to 1.
    return_stderr                   If return_stderr is set, this function
                                    will process the stdout and stderr streams
                                    from the shell command separately.  In
                                    such a case, the tuple returned by this
                                    function will consist of three values
                                    rather than just two: rc, stdout, stderr.
    fork                            Run the command string asynchronously
                                    (i.e. don't wait for status of the child
                                    process and don't try to get
                                    stdout/stderr).
    """

    # Assign default values to some of the arguments to this function.
    quiet = int(gm.dft(quiet, gp.get_stack_var('quiet', 0)))
    print_output = int(gm.dft(print_output, not quiet))
    show_err = int(show_err)
    global_ignore_err = gp.get_var_value(ignore_err, 1)
    stack_ignore_err = gp.get_stack_var('ignore_err', global_ignore_err)
    ignore_err = int(gm.dft(ignore_err, gm.dft(stack_ignore_err, 1)))

    err_msg = gv.svalid_value(command_string)
    if err_msg != "":
        raise ValueError(err_msg)

    if not quiet:
        gp.print_issuing(command_string, test_mode)

    if test_mode:
        if return_stderr:
            return 0, "", ""
        else:
            return 0, ""

    # Convert each list entry to a signed value.
    allowed_shell_rcs = [gm.to_signed(x) for x in allowed_shell_rcs]

    if return_stderr:
        stderr = subprocess.PIPE
    else:
        stderr = subprocess.STDOUT

    shell_rc = 0
    out_buf = ""
    err_buf = ""
    # Write all output to func_history_stdout rather than directly to stdout.
    # This allows us to decide what to print after all attempts to run the
    # command string have been made.  func_history_stdout will contain the
    # complete stdout history from the current invocation of this function.
    func_history_stdout = ""
    for attempt_num in range(1, max_attempts + 1):
        sub_proc = subprocess.Popen(command_string,
                                    bufsize=1,
                                    shell=True,
                                    executable='/bin/bash',
                                    stdout=subprocess.PIPE,
                                    stderr=stderr)
        out_buf = ""
        err_buf = ""
        # Output from this loop iteration is written to func_stdout for later
        # processing.
        func_stdout = ""
        if fork:
            break
        command_timed_out = False
        if time_out is not None:
            # Designate a SIGALRM handling function and set alarm.
            signal.signal(signal.SIGALRM, shell_cmd_timed_out)
            signal.alarm(time_out)
        try:
            if return_stderr:
                for line in sub_proc.stderr:
                    try:
                        err_buf += line
                    except TypeError:
                        line = line.decode("utf-8")
                        err_buf += line
                    if not print_output:
                        continue
                    func_stdout += line
            for line in sub_proc.stdout:
                try:
                    out_buf += line
                except TypeError:
                    line = line.decode("utf-8")
                    out_buf += line
                if not print_output:
                    continue
                func_stdout += line
        except IOError:
            command_timed_out = True
        sub_proc.communicate()
        shell_rc = sub_proc.returncode
        # Restore the original SIGALRM handler and clear the alarm.
        signal.signal(signal.SIGALRM, original_sigalrm_handler)
        signal.alarm(0)
        if shell_rc in allowed_shell_rcs:
            break
        err_msg = "The prior shell command failed.\n"
        if quiet:
            err_msg += gp.sprint_var(command_string)
        if command_timed_out:
            err_msg += gp.sprint_var(command_timed_out)
            err_msg += gp.sprint_var(time_out)
            err_msg += gp.sprint_varx("child_pid", sub_proc.pid)
        err_msg += gp.sprint_var(attempt_num)
        err_msg += gp.sprint_var(shell_rc, 1)
        err_msg += gp.sprint_var(allowed_shell_rcs, 1)
        if not print_output:
            if return_stderr:
                err_msg += "err_buf:\n" + err_buf
            err_msg += "out_buf:\n" + out_buf
        if show_err:
            if robot_env:
                func_stdout += grp.sprint_error_report(err_msg)
            else:
                func_stdout += gp.sprint_error_report(err_msg)
        func_history_stdout += func_stdout
        if attempt_num < max_attempts:
            func_history_stdout += gp.sprint_issuing("time.sleep("
                                                     + str(retry_sleep_time)
                                                     + ")")
            time.sleep(retry_sleep_time)

    if shell_rc not in allowed_shell_rcs:
        func_stdout = func_history_stdout

    if robot_env:
        grp.rprint(func_stdout)
    else:
        sys.stdout.write(func_stdout)
        sys.stdout.flush()

    if shell_rc not in allowed_shell_rcs:
        if not ignore_err:
            if robot_env:
                BuiltIn().fail(err_msg)
            else:
                raise ValueError("The prior shell command failed.\n")

    if return_stderr:
        return shell_rc, out_buf, err_buf
    else:
        return shell_rc, out_buf


def t_shell_cmd(command_string, **kwargs):
    r"""
    Search upward in the the call stack to obtain the test_mode argument, add
    it to kwargs and then call shell_cmd and return the result.

    See shell_cmd prolog for details on all arguments.
    """

    if 'test_mode' in kwargs:
        error_message = "Programmer error - test_mode is not a valid" +\
            " argument to this function."
        gp.print_error_report(error_message)
        exit(1)

    test_mode = gp.get_stack_var('test_mode',
                                 int(gp.get_var_value(None, 0, "test_mode")))
    kwargs['test_mode'] = test_mode

    return shell_cmd(command_string, **kwargs)
