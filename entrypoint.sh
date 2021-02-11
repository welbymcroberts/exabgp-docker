#!/bin/bash
ls -alh /run/exabgp.{in,out}

exec "$@"
