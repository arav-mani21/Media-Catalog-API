#!/bin/bash
set -e

yum update -y
yum install -y python3 python3-pip python3-venv

git clone --depth 1 https://github.com/arav-mani21/Media-Catalog-API.git /tmp/repo
sudo mv /tmp/repo/app /opt/media_catalog_app
sudo chown -R ec2-user:ec2-user /opt/media_catalog_app
rm -rf /tmp/repo

python3 -m venv /opt/media_catalog_app/venv
source /opt/media_catalog_app/venv/bin/activate
pip install -r /opt/media_catalog_app/requirements.txt

sudo tee /etc/systemd/system/media_catalog.service > /dev/null << 'EOF'
[Unit]
Description=Media Catalog FastAPI Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/media_catalog_app
ExecStart=/opt/media_catalog_app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable media_catalog
sudo systemctl start media_catalog