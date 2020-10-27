import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://localhost:8000')
print(s.put("key1","value1"))  
print(s.put("key2","value2"))  
print(s.get("key1"))  
print(s.get("key2"))  
print(s.get("key3"))  
print(s.put("key3","value3"))  
print(s.get("key3"))  
