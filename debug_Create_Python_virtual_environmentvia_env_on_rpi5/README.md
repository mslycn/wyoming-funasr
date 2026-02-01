# Deployment Service  Wyoming Protocol Server Test 

mini server.py Debug step by step

- server.py    

https://github.com/mslycn/wyoming-funasr/commit/fb5f2460060f0afaf901abe876897623c315b75d
  

- step 1. test mini server  run ok on rpi5    Wyoming Protocol only

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server1.py

https://github.com/mslycn/wyoming-funasr/commit/8ed61504372ea61268bab727085b4b2624342ff4

- step 2. test mini server ,connect to ha run ok on rpi5   add can connect to ha

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server2.py

homeassistant202405/.storage/core.config_entries
~~~
+  {"created_at":"2026-01-27T22:55:05.110411+00:00","data":{"host":"192.168.2.125","port":10800},"disabled_by":null,"discovery_keys":{},"domain":"wyoming","entry_id":"01KG0TNVCPTPDSN7YJMYTB78Q7","minor_version":1,"modified_at":"2026-01-27T22:55:05.110415+00:00","options":{},"pref_disable_new_entities":false,"pref_disable_polling":false,"source":"user","subentries":[],"title":"voxtral-wyoming","unique_id":null,"version":1}
~~~
homeassistant202405/.storage/core.entity_registry
~~~
+  {"created_at":"2026-01-27T22:55:05.110411+00:00","data":{"host":"192.168.2.125","port":10800},"disabled_by":null,"discovery_keys":{},"domain":"wyoming","entry_id":"01KG0TNVCPTPDSN7YJMYTB78Q7","minor_version":1,"modified_at":"2026-01-27T22:55:05.110415+00:00","options":{},"pref_disable_new_entities":false,"pref_disable_polling":false,"source":"user","subentries":[],"title":"voxtral-wyoming","unique_id":null,"version":1}
~~~

https://github.com/mslycn/wyoming-funasr/commit/c2c7c36f57c988d5cf6007151dce1053c9fcfda3

- step 3. test mini server ,connect to ha run ok ,load model by haon rpi5  add funasr mode

Speech Recognition (non Streaming)

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server3.py

https://github.com/mslycn/wyoming-funasr/commit/3b2a717e8985108d831a2b73a4e8610b6c1e1575

- step 4. test mini server ,connect to ha,load funasr model ,add ncpu=4 for rpi5, run ok , by ha on rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server4.py

https://github.com/mslycn/wyoming-funasr/commit/819b308d0827811fc62df5533de0d0a252159f1c

server.py https://github.com/mslycn/wyoming-funasr/commit/bcc8303e658bec0fb4bf7030cc80223a2924bafa

step 5. test mini server ,connect to ha run ok ,can discovered ,load model ,4 cpu used by haon rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server5.py


