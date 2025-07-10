import requests
from django.core.cache import cache

def post(gateway, path, json = {}, params = {}):
  url = f"https://{gateway.ip_address}:8443{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.post(url, json=json, params=params, headers=headers, verify="cacert.pem")

def get(gateway, path, params= {}):
  url = f"https://{gateway.ip_address}:8443{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.get(url, params= params, headers=headers, verify="cacert.pem")

def delete(gateway, path):
  url = f"https://{gateway.ip_address}:8443{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.delete(url, headers=headers, verify="cacert.pem")

def put(gateway, path, json={}):
  url = f"https://{gateway.ip_address}:8443{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.put(url, json=json, headers=headers, verify="cacert.pem")

def ping(gateway):
  try:
    response = requests.get(f"https://{gateway.ip_address}:8443/core-metadata/api/v3/ping")
    if response.status_code != 200:
      return False
    return True
  except Exception:
    return False
  
def get_user_api_token(gateway):
  key = f"api_jwt_token_{gateway.username}"
  token = cache.get(key)
  print("TOKEN LOGIN:", token)
  if token:
    return token
  print(gateway.ip_address)
  # Obtener las credenciales del usuario (pueden estar en un modelo relacionado)
  response = requests.post(f"http://{gateway.ip_address}:5000/login", json={
    "username": gateway.username,
    "password": gateway.get_password()
  })

  if response.status_code == 200:
    data = response.json()
    jwt = data['jwt']
    expires_in = data.get('expires_in', data["ttl"])
    cache.set(key, jwt, timeout=expires_in - 30)
    return jwt
  else:
    raise Exception(f"Could not get jwt for: {gateway.name}")