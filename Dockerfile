FROM deepnox:python-ta-lib

COPY  main.py lib /root/TWStockNotifier/
WORKDIR /root/TWStockNotifier
RUN  pip --no-cache-dir install -r requirements.txt

CMD ["python main.py"]
