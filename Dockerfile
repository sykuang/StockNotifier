FROM deepnox/python-ta-lib-pandas:1.4.3_talib0.4.24_python3.10.6_alpine3.16

COPY  main.py lib requirements.txt /root/TWStockNotifier/
WORKDIR /root/TWStockNotifier
RUN apk add --no-cache --virtual .build-deps \
  linux-headers \
  gcc \
  g++ \
  make \
  && pip --no-cache-dir install -r requirements.txt

CMD ["python main.py"]
