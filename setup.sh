#!/usr/bin/bash

(mkdir -p ~/.local/lib ~/.local/bin);
(curl -fL  https://github.com/cdr/code-server/releases/download/v3.12.0/code-server-3.12.0-linux-armv7l.tar.gz | tar -C ~/.local/lib -xz);
(mv ~/.local/lib/code-server-3.12.0-linux-armv7l ~/.local/lib/code-server-3.12.0);
(ln -s ~/.local/lib/code-server-3.12.0/bin/code-server ~/.local/bin/code-server);
(PATH="~/.local/bin:$PATH");

(cd /etc/systemd/system && echo "[Unit]
Description=Code Server AutoStart
After=network-online.target
Wants=network-online.target systemd-networkd-wait-online.service
[Service]
Type=simple
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
Restart=on-failure
ExecStart=/root/.local/bin/code-server
[Install]
WantedBy=multi-user.target" > code-server.service);
echo "Starting service...";
(systemctl daemon-reload && systemctl enable code-server.service && systemctl start code-server.service);