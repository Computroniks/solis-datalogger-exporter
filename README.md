<!-- 
SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
SPDX-License-Identifier: MIT
-->

# Solis datalogger exporter

A simple Prometheus exporter to scrape data from the web interface of
the Solis datalogging stick.

## Usage

To use the exporter run the following commands.

First clone the repo.

```
git clone https://github.com/Computroniks/solis-datalogger-exporter.git
```

Next create a virtual environment and install the required python
packages

```
cd solis-datalogger-exporter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Now we need to create the .env file that stores the configuration data.
First copy the example env file with the following command.

```
cp .env.example .env
```

Now open this file in a text editor and alter the values to match your
environment.

Now create a user to run the application and transfer ownership of all
files to that user. Ensure you run these commands from the root of the
repository and no where else!

```
sudo useradd --no-create-home --shell /bin/false solis-datalogger
chown -R solis-datalogger:solis-datalogger *
```

Now we need to create a service to ensure that the application keeps
running at all times. Create a file called `solis-datalogger.service` in
`/etc/systemd/system` and paste in the following. Note: you may need to
adjust the file paths to match your file structure.

```
[Unit]
Description=Solis inverter datalogging stick exporter
Wants=network-online.target
After=network-online.target

[Service]
User=solis-datalogger
Group=solis-datalogger
Type=simple
WorkingDirectory=/opt/solis-datalogger-exporter
ExecStart=/opt/solis-datalogger-exporter/venv/bin/python -m datalogger

[Install]
WantedBy=multi-user.target
```

You then need to run the following commands to reload the daemon, enable
the service to start on system restarts and then finally to start the
application.

```
sudo systemctl daemon-reload
sudo systemctl enable solis-datalogger.service
```

To check if the installation is successfull, you can run `sudo systemctl
status solis-datalogger.service` or navigate your browser to the IP and
port you are running the application on.

## Licence
This repo uses the [REUSE](https://reuse.software) standard in order to
communicate the correct licence for the file. For those unfamiliar with
the standard the licence for each file can be found in one of three
places. The licence will either be in a comment block at the top of the
file, in a `.license` file with the same name as the file, or in the
dep5 file located in the `.reuse` directory. If you are unsure of the
licencing terms please contact
[mnickson@sidingsmedia.com](mailto:mnickson@sidingsmedia.com).
All files committed to this repo must contain valid licencing
information or the pull request can not be accepted.
