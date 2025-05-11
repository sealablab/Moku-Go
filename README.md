# [Moku-Go](https://github.com/sealablab/Moku-Go)

The CLI you always wanted

# Layout

``` env.sh
export MOKU_DATA_PATH=mokudata-601
export MOKU_IP=10.0.44.219
```
# ENV Vars
## MOKU-DATA-PATH: `./mokudata-601`
```
### mokudata-601.tar
```
johnycsh@DRP-e1 Moku-Go % md5sum ./mokudata-601/mokudata-601.tar
a88872e8e032f4a45e8f1ce8e98c765a ./mokudata-601/mokudata-601.tar
johnycsh@DRP-e1 Moku-Go % ls -lh ./mokudata-601/mokudata-601.tar
-rw-r--r--@ 1 johnycsh  staff   595M May 11 15:30 ./mokudata-601/mokudata-601.tar
```
## Debugging:
I get the following error
 ```  File "osc.py"
       data = i.get_data()
AttributeError: 'NoneType' object has no attribute 'get_data'
```
You probably need to source ./env.sh and try again

