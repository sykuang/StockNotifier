FROM deepnox/python-ta-lib-pandas:1.4.3_talib0.4.24_python3.10.6_alpine3.16

WORKDIR /root/TWStockNotifier
# install zsh and gcc for python modules
COPY requirements.txt /root/TWStockNotifier/
RUN apk add --no-cache --virtual .build-deps \
  linux-headers \
  gcc \
  g++ \
  make && \
  pip --no-cache-dir install -r requirements.txt && \
# Add yacron for running as server
  pip --no-cache-dir install yacron

COPY  main.py docker/crontab.yaml example/config.json /root/TWStockNotifier/
COPY  lib /root/TWStockNotifier/lib


CMD ["yacron", "-c", "/root/TWStockNotifier//crontab.yaml"]
