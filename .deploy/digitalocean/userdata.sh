#!/bin/bash

# Create swapspace
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# SSH deploy key setup
# tbdrenzil - manually create ~/.ssh/id_gitdeploykey
chmod 600 ~/.ssh/id_gitdeploykey
eval "$(ssh-agent -s)"
touch ~/.ssh/config
echo "Host *
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_gitdeploykey
" >> ~/.ssh/config
ssh-add ~/.ssh/id_gitdeploykey

# Clone git repo
cd ~
ssh -o "StrictHostKeyChecking no" github.com
git clone git@github.com:rappo-ai/landerbot-demo.git
chmod -R g+w ~/landerbot-demo

# update credentials
# tbdrenzil - manually create ~/landerbot-demo/.env
# tbdrenzil - [OPTIONAL] manually create create ~/landerbot-demo/.deploy/nginx/.env from /landerbot-demo/.deploy/nginx/.env.template and update the env variables as needed
# tbdrenzil - [OPTIONAL] manually add GCP service account json credentials to ~/landerbot-demo/.deploy/mgob/secrets/ and update bucket name in ~/landerbot-demo/.deploy/mgob/hourly.yml

# launch docker
cd ~/landerbot-demo
docker-compose -f docker-compose.base.yml -f docker-compose.yml up --build --force-recreate -d
