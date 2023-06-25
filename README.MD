# provides a convenient and efficient solution for capturing and analyzing system activity logs using Procmon and converting them to the pandas compatible Parquet file format (2% of the original pml file size)


## pip install procmondf

### Tested against Windows 10 / Python 3.10 / Anaconda 


The ProcMonDf class and its associated functions are used for logging and analyzing system processes and 
events using Microsoft's Procmon https://learn.microsoft.com/en-us/sysinternals/downloads/procmon utility. 
Procmon is a Windows-based tool that monitors and captures real-time system activity, 
including file system and registry operations, process and thread activity, network activity, and more.

The ProcMonDf class provides a convenient way to start and stop logging with Procmon, 
save the log as a Parquet file, and optionally return the log as a pandas DataFrame. 
It leverages the functionality of the Procmon utility and combines 
it with the data processing capabilities of pandas and 
Parquet file format for efficient storage (between 1% to 5% of the original pml file size) and analysis.
600.000 rows require about 5 mb of disk space.

This functionality might be interesting for developers, system administrators, and analysts who need to track 
and analyze system behavior, diagnose issues, understand resource usage patterns, 
or monitor software performance. 
By using the ProcMonDf class, they can automate the process of capturing system activity logs, 
convert them to a structured DataFrame, and perform further analysis, filtering, 
or visualization using the powerful tools available in the pandas ecosystem.

The advantages of using ProcMonDf and the associated functions include:

### Simplified interface: 

The class encapsulates the complex logic required to start and stop Procmon logging, 
convert logs to Parquet format, and manage temporary files.

### Data processing capabilities: 

The captured logs are converted into a structured DataFrame, allowing users to leverage the powerful data manipulation and analysis functionalities provided by pandas.

### Storage efficiency: 

The logs are saved in Parquet format, which offers a columnar storage layout and compression, resulting in reduced storage space requirements and improved query performance.

### Flexibility and extensibility: 

Users can customize the logging parameters and additional arguments 
passed to Procmon to suit their specific requirements.

### Integration with existing workflows: 

The ability to return the log as a DataFrame allows users to seamlessly integrate it 
into their existing data analysis pipelines or leverage other libraries and tools compatible with pandas.

```python
class ProcMonDf:
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
        
```