apt install make
apt install emacs-nox
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04

sudo apt update
# Next, install a few prerequisite packages which let apt use packages over HTTPS:

sudo apt install apt-transport-https ca-certificates curl software-properties-common
# Then add the GPG key for the official Docker repository to your system:

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# Add the Docker repository to APT sources:

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
# This will also update our package database with the Docker packages from the newly added repo.

# Make sure you are about to install from the Docker repo instead of the default Ubuntu repo:

apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker

mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.3.3/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
# Next, set the correct permissions so that the docker compose command is executable:

chmod +x ~/.docker/cli-plugins/docker-compose
# To verify that the installation was successful, you can run:

docker compose version

curl --proto '=https' --tlsv1.3 https://sh.rustup.rs -sSf | sh
source $HOME/.cargo/env
apt install libssl-dev
apt install pkg-config

cargo install --locked gptcommit
echo "type 'gptcommit install' and follow api key instructions"
apt install moreutils
