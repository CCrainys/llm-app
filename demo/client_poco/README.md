# README

## Prerequisite

Install POCO:

```
sudo apt-get install openssl libssl-dev
sudo apt install build-essential gdb cmake git
sudo apt-get install libiodbc2 libiodbc2-dev libmysqlclient-dev libpq-dev
cd /tmp
git clone -b master https://github.com/pocoproject/poco.git
cd poco && mkdir build && cd build && cmake ..
cmake --build . --config Release -j
sudo cmake --build . --target install
```
