# README

## Prerequisite

Install POCO:

```bash
sudo apt-get install -y openssl libssl-dev build-essential gdb cmake git libiodbc2 libiodbc2-dev libmysqlclient-dev libpq-dev
cd /tmp
git clone -b master https://github.com/pocoproject/poco.git
cd poco && mkdir -p build && cd build && cmake ..
cmake --build . --config Release -j
sudo cmake --build . --target install
```

You might need to add `/usr/local/lib` to LD_LIBRARY_PATH:

```bash
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/local/lib" >> ~/.zshrc
exec zsh
```

Install spdlog:

```bash
sudo apt install -y libspdlog-dev
```
