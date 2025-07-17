import requests
from django.core.cache import cache

def post(gateway, path, json = {}, params = {}):
  url = f"https://{gateway.ip_address}:{gateway.api_port}{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.post(url, json=json, params=params, headers=headers)

def get(gateway, path, params= {}):
  url = f"https://{gateway.ip_address}:{gateway.api_port}{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.get(url, params= params, headers=headers)

def delete(gateway, path):
  url = f"https://{gateway.ip_address}:{gateway.api_port}{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.delete(url, headers=headers)

def put(gateway, path, json={}):
  url = f"https://{gateway.ip_address}:{gateway.api_port}{path}"
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  return requests.put(url, json=json, headers=headers)

def ping(gateway, timeout=5):
  jwt= get_user_api_token(gateway)
  headers = {
    "Authorization": f"Bearer {jwt}"
  }
  try:
    response = requests.get(f"https://{gateway.ip_address}:{gateway.api_port}/core-metadata/api/v3/ping",headers=headers, timeout=timeout)
    if response.status_code != 200:
      return False
    return True
  except Exception:
    return False
  
def get_user_api_token(gateway):
  key = f"api_jwt_token_{gateway.username}"
  token = cache.get(key)
  if token:
    return token

  try:
    login_url = f"https://{gateway.ip_address}:{gateway.api_port}/vault/v1/auth/userpass/login/{gateway.username}"
    login_payload = {"password": gateway.get_password()}
    login_resp = requests.post(login_url, json=login_payload, timeout=10)
    login_resp.raise_for_status()
  except requests.RequestException as e:
    raise Exception(f"Login failed for {gateway.name}: {e}") from e

  auth_data = login_resp.json().get("auth")
  if not auth_data or "client_token" not in auth_data:
    raise Exception(f"Invalid login response for {gateway.name}: {login_resp.text}")

  secret_store_token = auth_data["client_token"]

  headers = {"Authorization": f"Bearer {secret_store_token}"}
  token_url = f"https://{gateway.ip_address}:{gateway.api_port}/vault/v1/identity/oidc/token/{gateway.username}"

  try:
    token_resp = requests.get(token_url, headers=headers, timeout=10)
    token_resp.raise_for_status()
  except requests.RequestException as e:
    raise Exception(f"Could not get JWT for {gateway.name}: {e}") from e

  data = token_resp.json().get("data")
  if not data or "token" not in data:
    raise Exception(f"Invalid token response for {gateway.name}: {token_resp.text}")

  jwt = data["token"]
  expires_in = data.get("ttl")
  cache_timeout = max(expires_in - 30, 60)  # cachea mínimo 60 segundos

  cache.set(key, jwt, timeout=cache_timeout)

  return jwt
