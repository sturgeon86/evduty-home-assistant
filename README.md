# evduty-home-assistant
EVduty Home Assistant integration



## Development

### Test locally
```shell
    make install
    make test
```

### Run locally
```shell
# from ha core repo, setup ha core
script/setup
source venv/bin/activate

# create a symlink in config folder to this folder
ln -s ../evduty-home-assistant/custom_components config/custom_components

# run
hass -c config
```