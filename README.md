# sb2mqtt

Bluetooth Advertise packet を解析してMQTTサーバに情報をpublishする。

## 設定
```
$ export MQTT_HOST=localhost
$ export MQTT_PORT=1883
```

## 実行
```
$ python3 sb2mqtt.py
```

## サービスとして実行

### 設定ファイルの配置

- sbm2qtt ファイルを/etc/default/ にコピー
- sb2mqtt.service ファイルを/etc/systemd/system/ にコピー

### 有効化
```
$ sudo systemctl daemon-reload
$ sudo systemctl enable sb2matt
$ sudo systemctl start sb2matt
```
