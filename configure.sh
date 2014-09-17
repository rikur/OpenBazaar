#!/bin/bash

#
# configure.sh - Setup your OpenBazaar development environment in one step.
#
# If you are an Ubuntu or MacOSX user, you can try configuring/installing
# OpenBazaar by simply executing this script instead of following the build
# instructions in the OpenBazaar Wiki:
# https://github.com/OpenBazaar/OpenBazaar/wiki/Build-Instructions
#
# This script will only get better as its tested on more development environments
# if you can't modify it to make it better, please open an issue with a full
# error report at https://github.com/OpenBazaar/OpenBazaar/issues/new
#

#exit on error
set -e

function command_exists {
  #this should be a very portable way of checking if something is on the path
  #usage: "if command_exists foo; then echo it exists; fi"
  type "$1" &> /dev/null
}

function brewDoctor {
    if ! brew doctor; then
      echo ""
      echo "'brew doctor' did not exit cleanly! This may be okay. Read above."
      echo ""
      read -p "Press [Enter] to continue anyway or [ctrl + c] to exit and do what the doctor says..."
    fi
}

function brewUpgrade {
    if ! brew upgrade; then
      echo ""
      echo "There were errors when attempting to 'brew upgrade' and there could be issues with the installation of OpenBazaar."
      echo ""
      read -p "Press [Enter] to continue anyway or [ctrl + c] to exit and fix those errors."
    fi
}

function installMac {
  #print commands (useful for debugging)
  #set -x  #disabled because the echos and stdout are verbose enough to see progress

  #install brew if it is not installed, otherwise upgrade it
  if ! command_exists brew ; then
    echo "installing brew..."
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
  else
    echo "updating, upgrading, checking brew..."
    brew update
    brewDoctor
    brewUpgrade 
    brew prune
  fi
  
  #install gpg/sqlite3/python/wget if they aren't installed
  for dep in gpg sqlite3 python wget
  do
    if ! command_exists $dep ; then
      brew install $dep
    fi
  done

  #more brew prerequisites
  brew install openssl zmq

  #python prerequisites
  #python may be owned by root, or it may be owned by the user
  PYTHON_OWNER=$(stat -n -f %u `which python`)
  if [ "$PYTHON_OWNER" == "0" ]; then
    #root owns python
    EASY_INSTALL="sudo easy_install"
    PIP="sudo pip"
  else
    EASY_INSTALL="easy_install"
    PIP="pip"
  fi

  #install pip if it is not installed
  if ! command_exists pip ; then
    $EASY_INSTALL pip
  fi

  #install python's virtualenv if it is not installed
  if ! command_exists virtualenv ; then
    $PIP install virtualenv
  fi

  #create a virtualenv for OpenBazaar
  if [ ! -d "./env" ]; then
    virtualenv env
  fi

  # set compile flags for brew's openssl instead of using brew link --force
  export CFLAGS="-I$(brew --prefix openssl)/include"
  export LDFLAGS="-L$(brew --prefix openssl)/lib"

  #install python deps inside our virtualenv
  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

  doneMessage
}

function doneMessage {
echo ""
echo "OpenBazaar configuration finished."
echo "type './run.sh; tail -f logs/production.log' to start your OpenBazaar servent instance and monitor logging output."
echo ""
echo ""
echo ""
echo ""
}

function installUbuntu {
  #print commands
  set -x

  sudo apt-get update
  sudo apt-get install python-pip build-essential python-zmq rng-tools
  sudo apt-get install python-dev python-pip g++ libjpeg-dev zlib1g-dev sqlite3 openssl
  sudo apt-get install alien libssl-dev python-virtualenv lintian libjs-jquery

  if [ ! -d "./env" ]; then
    virtualenv env
  fi

  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

  doneMessage
}

function installArch {
  #print commands
  set -x

  sudo pacman -Sy
  #sudo pacman -S --needed base-devel #Can conflict with multilib packages. Uncomment this line if you don't already have base-devel installed
  sudo pacman -S --needed python2 python2-pip python2-virtualenv python2-pyzmq rng-tools libjpeg zlib sqlite3 openssl

  if [ ! -d "./env" ]; then
    virtualenv2 env
  fi

  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

  doneMessage
}

function installPortage {
  #print commands
  set -x

  sudo emerge -an dev-lang/python:2.7 dev-python/pip pyzmq rng-tools gcc jpeg zlib sqlite3 openssl dev-python/virtualenv
  # FIXME: on gentoo install as user, because otherwise
  # /usr/lib/python-exec/python-exec* gets overwritten by nose,
  # killing most Python programs.
  pushd pysqlcipher
  python2.7 setup.py install --user
  popd
  pip install --user -r requirements.txt
  doneMessage
}

function installFedora {
  #print commands
  set -x

  sudo yum install -y http://linux.ringingliberty.com/bitcoin/f18/x86_64/bitcoin-release-1-4.noarch.rpm

  sudo yum -y install python-pip python-zmq rng-tools openssl \
  openssl-devel alien python-virtualenv make automake gcc gcc-c++ \
  kernel-devel python-devel openjpeg-devel zlib-devel sqlite \
   zeromq-devel zeromq python python-qt4 openssl-compat-bitcoin-libs

  if [ ! -d "./env" ]; then
    virtualenv env
  fi

  ./env/bin/pip install ./pysqlcipher
  ./env/bin/pip install -r requirements.txt

  doneMessage
}

if [[ $OSTYPE == darwin* ]] ; then
  installMac
elif [[ $OSTYPE == linux-gnu || $OSTYPE == linux-gnueabihf ]]; then
  if [ -f /etc/arch-release ]; then
    installArch
  elif [ -f /etc/gentoo-release ]; then
    installPortage
  elif [ -f /etc/fedora-release ]; then
    installFedora
  else
    installUbuntu
  fi
fi
