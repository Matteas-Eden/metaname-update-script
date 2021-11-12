# Metaname DNS Record Update Script
A small Python script to update a single A record on Metaname's servers.
Configuration variables are loaded in from a local `.env` file, and a template
service file for use with systemd is included.

## Configuration
In order to configure the script, you may copy the `.env.template` file into
`.env` and populate the fields within. Here's a breakdown of the variables:

| Name              | Description                                                    |
| ----              | -----------                                                    |
| ACCOUNT_REFERENCE | The 4 digit code used to uniquely identify a Metaname account. |
| API_KEY           | The API key provided to you by Metaname.                       |
| RECORD_NAME       | The name of the A record to be updated on Metaname.            |
| LOGGING_FILE      | The name of the file to log to.                                |
| IP_STORE_NAME     | The name of the file to store the last known IP in.            |
| DOMAIN_NAME       | The domain whose DNS table is being updated.                   |

## Usage
Using the script is simple. You may run the script manually, or you can
configure the script to run on boot via systemd. For either usage, passing the
`-s` or `--silent` parameters suppresses logging.

### Manual
To run the script manually, simply execute via the command line:
```
chmod +x metanameUpdateScript.py
./metanameUpdateScript.py
```

### On Boot
If you wish to execute the script on boot alongside other systemd services,
then you can use the `metaname-update-script.service.template` included in the
repository. It looks like this:
```
[Unit]
Description=Updates Metaname DNS Record with Public IP
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /path/to/script.py
WorkingDirectory=/path/to/
User=<user>

[Install]
WantedBy=multi-user.target
```
You're going to want to fill out `/path/to/script.py` with the *absolute* path
on your machine to where the `metanameUpdateScript.py` script is located. You
also need to replace `<user>` with the name of the user account who will be
executing the service. Then, simply enable it like you would any other systemd
service:

`systemctl enable metaname-update-script`

## License
This software is provided under the MIT license.
