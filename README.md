# netem

network emulation for Linux

## How to use

### Reset configuration

```shell
python3 netem.py reset
```

### Manual use

First, you need to adjust `cfg.json`. `-1` value mean unset

```json
{
    "hosts": [
        {
            "ip_address": "192.168.17.163",
            "interface": "ens33",
            "latency": 50,
            "jitter": -1,
            "bandwidth": -1
        },
        {
            "ip_address": "192.168.17.162",
            "interface": "ens33",
            "latency": 700,
            "jitter": -1,
            "bandwidth": -1
        }
    ]
}
```

After adjusting the configuration, you can run the code

```shell
python3 netem.py
```

