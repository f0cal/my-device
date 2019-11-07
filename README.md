# Quick start

```bash
VENV_DIR=_venv
curl bootstrap.f0cal.com/master | python3 - git -v ${VENV_DIR}
f0cal my-device --help
```

# About

`f0cal/my-device` implements a CLI front-end to various vendor-supplied
operating system installers and manual install procedures. The goal of the
project is to normalize the install process, making it consistent across vendors
and hardware. Everything should be as simple as calling the following from a
companion machine:

```bash
f0cal my-device image install \
  --image ... \
  --device-type ... \
  ...
```

Supported OSes include Ubuntu, Debian, Arch, NVidia L4T, Google Mendel,
Raspbian, and various other Linux flavors.

Supported devices include Raspberry Pi, NVidia Jetson boards, Google Coral, and
others.

# Learn more

[f0cal.com/docs](f0cal.com/docs#my-device)

