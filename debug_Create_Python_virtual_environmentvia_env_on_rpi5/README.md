

mini server.py Debug step by step

step 1. test mini server  run ok on rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server1.py

step 2. test mini server ,connect to ha run ok on rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server2.py

homeassistant202405/.storage/core.config_entries
~~~
+  {"created_at":"2026-01-27T22:55:05.110411+00:00","data":{"host":"192.168.2.125","port":10800},"disabled_by":null,"discovery_keys":{},"domain":"wyoming","entry_id":"01KG0TNVCPTPDSN7YJMYTB78Q7","minor_version":1,"modified_at":"2026-01-27T22:55:05.110415+00:00","options":{},"pref_disable_new_entities":false,"pref_disable_polling":false,"source":"user","subentries":[],"title":"voxtral-wyoming","unique_id":null,"version":1}
~~~
homeassistant202405/.storage/core.entity_registry
~~~
+  {"created_at":"2026-01-27T22:55:05.110411+00:00","data":{"host":"192.168.2.125","port":10800},"disabled_by":null,"discovery_keys":{},"domain":"wyoming","entry_id":"01KG0TNVCPTPDSN7YJMYTB78Q7","minor_version":1,"modified_at":"2026-01-27T22:55:05.110415+00:00","options":{},"pref_disable_new_entities":false,"pref_disable_polling":false,"source":"user","subentries":[],"title":"voxtral-wyoming","unique_id":null,"version":1}
~~~

step 3. test mini server ,connect to ha run ok ,load model by haon rpi5

Speech Recognition (non Streaming)

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server3.py

step 4. test mini server ,connect to ha run ok ,can discovered , by haon rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server4.py

step 5. test mini server ,connect to ha run ok ,can discovered ,load model ,4 cpu used by haon rpi5

https://github.com/mslycn/wyoming-funasr/blob/main/debug_Create_Python_virtual_environmentvia_env_on_rpi5/server5.py


