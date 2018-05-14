# MultiDomain Sync for Ranger
This repo has the code and instructions needed to sync multiple users and groups from different AD domains. Currently, Ranger only syncs one domain at a time. It utilizes Ranger's sync from a file using JSON format.
Reference: https://cwiki.apache.org/confluence/display/RANGER/File+Source+User+Group+Sync+process

With the CSV Option you can have the Usersync daemon ingest the file automatically. When Using JSON, you have run a crontab job as per the documentation listed above

### Assumptions and limitations:

  - It only syncs from AD, no LDAP support.
  - OS visibility to the different domains is already configured.
  - You have the groups you need to sync, it will sync the groups and the users belonging to those groups. Similar behavior to Ranger sync groups first with user map.
  - Python ldap and python-ldap packages are installed.  
  - It will not handle duplicate users, the domain with the higher priority will be synced first. Duplicate users on other domains will be ignored.

### Password Encryption:
To avoid storing passwords in clear text. Use the script encryptpassworrd.py to encrypt the passwords before storing them in the configs file

### Instructions:

  - Edit the configuration file and define your domains there.
  - By default it will dump JSON, use the -f option to dump CSV
  - Use the -h for the usersync to find the options. Adjust the config, output, logs files accordingly to your needs.
  - Change Ranger configuration file to point to the file generated.
  - Add the script to crontab with your preferred times to make sure changes are reflected.

### Script options:

#### Options:
  * -h, --help            Show this help message and exit
  * -c CONFIGS, --config-file=CONFIGS Configs file to read from. Must follow JSON format
  * -l LOGFILE, --log-file=LOGFILE Log file location
  * -o OUTPUTFILE, --output-file=OUTPUTFILE Output file location
  * -d, --debug           Debugging logs
  * -f FORMAT, --output-format=FORMAT, Output format: either JSON or CSV. Default JSON.
