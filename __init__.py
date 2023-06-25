import os, subprocess, tempfile, pyarrow, os.path

import pandas as pd
from getfilenuitkapython import get_filepath
from kthread_sleep import sleep
from subprocess_alive import is_process_alive
from touchtouch import touch
from datetime import datetime  # https://man7.org/linux/man-pages/man3/strftime.3.html
import numpy as np

procmonexe = get_filepath("Procmon.exe")


def get_tmpfile(suffix: str = ".pmc") -> str:
    r"""
    Returns a temporary file path with the specified suffix.

    Args:
        suffix (str): The suffix for the temporary file. Default is ".pmc".

    Returns:
        str: The path to the temporary file.
    """
    tfp = tempfile.NamedTemporaryFile(delete=True, suffix=suffix)
    filename = os.path.normpath(tfp.name)
    tfp.close()
    return filename


def run_proc(command: list | str) -> subprocess.Popen:
    """
    Runs a subprocess with the specified command.

    Args:
        command (list | str): The command to execute as a list of arguments or a single string.

    Returns:
        subprocess.Popen: The Popen object representing the subprocess.
    """
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    creationflags = subprocess.CREATE_NO_WINDOW
    invisibledict = {
        "startupinfo": startupinfo,
        "creationflags": creationflags,
        "start_new_session": True,
    }
    return subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        bufsize=0,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **invisibledict,
    )


def start_logging(pmlfile: str, *args) -> subprocess.Popen:
    """
    Starts the logging process with the specified PML file and additional arguments.

    Args:
        pmlfile (str): The path to the PML file for logging.
        *args: Additional arguments to be passed to the logging process.

    Returns:
        subprocess.Popen: The Popen object representing the logging process.
    """
    command = [
        procmonexe,
        "/accepteula",
        "/NoFilter",
        "/Runtime",
        "300",
        "/quiet",
        "/BackingFile",
        pmlfile,
        "/Minimized",
        *args,
    ]
    return run_proc(command)


def stop_logging_and_get_csv(pid: int, pmlfile: str, csvfile: str, *args) -> None:
    """
    Stops the logging process associated with the specified PID, saves the log as a CSV file, and terminates the process.

    Args:
        pid (int): The PID (Process ID) of the logging process.
        pmlfile (str): The path to the PML file associated with the logging process.
        csvfile (str): The path to save the log as a CSV file.
        *args: Additional arguments to be passed for saving the log.

    Returns:
        None
    """
    command = [procmonexe, "/accepteula", "/Terminate", "/Minimized", "/quiet"]
    _ = run_proc(command)
    while is_process_alive(pid):
        sleep(1)
    command2 = [
        procmonexe,
        "/accepteula",
        "/OpenLog",
        pmlfile,
        "/SaveAs",
        csvfile,
        "/Minimized",
        "/quiet",
        *args,
    ]
    p2 = run_proc(command2)
    while is_process_alive(p2.pid):
        sleep(1)


def convert_to_pqt(file_path: str, pqt_file: str) -> None:
    """
    Converts a CSV file to Parquet format.

    Args:
        file_path (str): The path to the CSV file.
        pqt_file (str): The path to save the Parquet file.

    Returns:
        None
    """
    last_modified_datetime = datetime.fromtimestamp(os.path.getmtime(file_path))
    day_created = last_modified_datetime.date()

    df = pd.DataFrame(
        pd.read_table(
            file_path,
            sep=",",
            names=[
                "Time of Day",
                "Process Name",
                "PID",
                "Operation",
                "Path",
                "Result",
                "Detail",
            ],
            parse_dates=["Time of Day"],
            date_format="%I:%M:%S.%f %p",
            header=0,
            dtype={
                "Process Name": "category",
                "PID": np.uint16,
                "Operation": "category",
                "Path": "category",
                "Result": "category",
                "Detail": "category",
            },
            engine="pyarrow",
            cache_dates=True,
        )
    )
    df.columns = [
        f'aa_{x.lower().replace(" ", "-").replace("-", "_")}' for x in df.columns
    ]
    df.aa_time_of_day = df.aa_time_of_day.apply(
        lambda x: datetime.combine(day_created, x.time())
    )
    df.to_parquet(pqt_file)


class ProcMonDf:
    def __init__(self, output: str):
        r"""
        Initializes a ProcMonDf object.

        Args:
            output (str): The path to the output Parquet file. Doesn't have to exist yet.

        Returns:
            None

        Example:
            from procmondf import ProcMonDf
            pm = ProcMonDf("c:\\proggi.pqt")
            pm.start_logging()
            # when you are done, use the following command to stop logging
            df=pm.stop_logging(deltmp=True, returndf=True)

            print(df[:5].to_string())
              aa_time_of_day aa_process_name  aa_pid   aa_operation                                                                                          aa_path       aa_result                           aa_detail
              0 2023-06-25 09:55:29.951767    Explorer.EXE    3904     RegOpenKey                HKCU\Software\Classes\CLSID\{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}\InprocServer32  NAME NOT FOUND                Desired Access: Read
              1 2023-06-25 09:55:29.951783    Explorer.EXE    3904    RegQueryKey                                                HKCR\CLSID\{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}         SUCCESS  Query: HandleTags, HandleTags: 0x0
              2 2023-06-25 09:55:29.951792    Explorer.EXE    3904     RegOpenKey                                 HKCR\CLSID\{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}\InprocServer32         SUCCESS                Desired Access: Read
              3 2023-06-25 09:55:29.951836    Explorer.EXE    3904    RegQueryKey  HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\SessionInfo\1\ApplicationViewManagement         SUCCESS  Query: HandleTags, HandleTags: 0x0
              4 2023-06-25 09:55:29.951837   Procmon64.exe   11160  RegQueryValue          HKLM\System\CurrentControlSet\Control\WMI\Securityxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   NAME NOT FOUND                         Length: 528

        """

        self.output = os.path.normpath(output)
        touch(output)
        self.pmlfile = get_tmpfile(suffix=".pml")
        self.csvfile = get_tmpfile(suffix=".csv")
        self._log_proc = None

    def start_logging(self, *args) -> None:
        """
        Starts the logging process.

        Args:
            *args: Additional arguments to be passed for logging. (procmon.exe cli)

        Returns:
            None
        """
        self._log_proc = start_logging(pmlfile=self.pmlfile, *args)

    def stop_logging(
        self, deltmp: bool = True, returndf: bool = True, *args
    ) -> None | pd.DataFrame:
        """
        Stops the logging process, saves the log as a Parquet file, and optionally returns a DataFrame.

        Args:
            deltmp (bool): Whether to delete the temporary files (default is True).
            returndf (bool): Whether to return a DataFrame from the Parquet file (default is True).
            *args: Additional arguments to be passed for saving the log.  (procmon.exe cli)

        Returns:
            None or pd.DataFrame: The DataFrame read from the Parquet file if returndf is True, else None.
        """
        stop_logging_and_get_csv(
            self._log_proc.pid, pmlfile=self.pmlfile, csvfile=self.csvfile, *args
        )
        convert_to_pqt(self.csvfile, self.output)

        if deltmp:
            try:
                os.remove(self.csvfile)
            except Exception:
                print(f"{self.csvfile} could not be removed")
            try:
                os.remove(self.pmlfile)
            except Exception:
                print(f"{self.pmlfile} could not be removed")
        else:
            print(self.csvfile)
            print(self.pmlfile)

        if returndf:
            return pd.read_parquet(self.output)
