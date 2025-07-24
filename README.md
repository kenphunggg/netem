# netem

network emulation for Linux

## How to use

### Reset configuration

```shell
python3 netem.py reset
```

### Manual use

First, you need to adjust `cfg.json`.

Unit of `latency` and `jitter` is `ms` stands for miliseconds

Unit of `bandwidth` is `kbit` stands for `kilobit/sec`

> [!NOTE]
> 8 kilobit/sec = 1 kilobyte/sec

```json
{
    "interface": "ens33",
    "hosts": [
        {
            "ip_address": "192.168.17.162",
            "latency": 200,
            "jitter": 20,
            "bandwidth": 600
        },
        {
            "ip_address": "192.168.17.163",
            "latency": 50,
            "jitter": 10,
            "bandwidth": 12000
        }
    ]
}
```

After adjusting the configuration, you can run the code

```shell
python3 netem.py
```

