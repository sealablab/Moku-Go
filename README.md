# [Moku-Go](https://github.com/sealablab/Moku-Go)

The CLI you always wanted

# Installation
We use [uv](https://docs.astral.sh/uv/) for project management, so
```
git clone git@github.com:sealablab/Moku-Go.git
cd  Moku-Go
johnycsh@DRP-e1 Moku-Go % uv sync
```

# Running
```
johnycsh@DRP-e1 Moku-Go % uv run hello.py
johnycsh@DRP-e1 Moku-Go % uv run osc.py
```

# Where are the (moku) bitstreams? 
You can find them in a file named `mokudata-601.tar`
By convention (in this project), we keep it here:
### `mokudata-601.tar`
```
johnycsh@DRP-e1 Moku-Go/mokudata-601/ % md5sum .mokudata-601.tar a88872e8e032f4a45e8f1ce8e98c765a
johnycsh@DRP-e1 Moku-Go.mokudata-601/ % ls -lh ./mokudata-601/mokudata-601.tar
-rw-r--r--@ 1 johnycsh  staff   595M May 11 15:30 ./mokudata-601/mokudata-601.tar
```
(Yes, the moku provided bitstreams are about 600Mb)



``` env.sh
export MOKU_DATA_PATH=mokudata-601
export MOKU_IP=10.0.44.219
```
# ENV Vars
## MOKU-DATA-PATH: `./mokudata-601`

# Debugging:
I get the following error
 ```  File "osc.py"
       data = i.get_data()
AttributeError: 'NoneType' object has no attribute 'get_data'
```
Moku-Go was unable to locate your upstream bitstreams. 
Check your `MOKU_DATA_PATH` Env var, and try again.

