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
- sb2mqtt.service ファイル中の [Service]セクションのの値を修正
- sb2mqtt.service ファイルを/etc/systemd/system/ にコピー

### 有効化
```
$ sudo systemctl daemon-reload
$ sudo systemctl enable sb2matt
$ sudo systemctl start sb2matt
```
## Home Assistant統合

SwitchBot bluetooth統合を使う。

### センサーの追加

このソフトウェアを利用する必要はない。

SwitchBot Plugを利用している場合、電力(W)センサーを利用できる。
Integral統合を利用して電力量センサーを追加する。

configuration.yamlを編集し、Integralセンサ-を構成する。
```
sensor:
  - platform: integration
    source: sensor.plug_mini_jp_xxxx_power
    name: plug_mini_jp_xxxx_energy
    unit_prefix: k
    round: 2
    max_sub_interval:
      minutes: 5  
```

### エネルギー設定

1. Home Assistantのダッシュボードに　エネルギーを追加する。
2. エネルギーを表示し、右上のハンバーガーメニューをクリックし、エネルギーの設定メニューを選択する。
3. 個々のデバイスパネルから、デバイスの追加をクリックする。
4. 電力量センサーを追加する。

