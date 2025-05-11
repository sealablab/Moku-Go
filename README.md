# [Moku-Go](https://github.com/sealablab/Moku-Go)

The CLI you always wanted

# Layout

``` env.sh
export MOKU_DATA_PATH=mokudata-601
export MOKU_IP=10.0.44.219
```
# ENV Vars
## MOKU-DATA-PATH: `./mokudata-601`
If you are following my lead, you will have the latest set of instrument files located in:
```


## Debugging:
I get the following error
 ```  File "osc.py"
       data = i.get_data()
AttributeError: 'NoneType' object has no attribute 'get_data'
```
You probably need to source ./env.sh and try again

