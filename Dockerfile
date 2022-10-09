FROM deepnox/python-ta-lib:0.4.24_python3.10_alpine3.16

COPY  main.py lib /root/TWStockNotifier/
WORKDIR /root/TWStockNotifier
RUN  pip --no-cache-dir install -r requirements.txt

CMD ["python main.py"]
