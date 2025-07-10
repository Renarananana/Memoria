from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VAULT_URL = "http://secret-store:8200"

@app.route("/login", methods=["POST"])
def login():
  data = request.json
  username = data.get("username")
  password = data.get("password")
  if not username or not password:
    return jsonify({"error": "Missing username or password"}), 400

  # 1. Login a Vault con userpass
  print(VAULT_URL)
  vault_resp = requests.post(
    f"{VAULT_URL}/v1/auth/userpass/login/{username}",
    json={"password": password}
  )
  if vault_resp.status_code != 200:
    return jsonify({"error": "Invalid credentials"}), 401

  vault_token = vault_resp.json()["auth"]["client_token"]

  # 2. Intercambiar token Vault por JWT en API Gateway
  resp = requests.get(
    f"{VAULT_URL}/v1/identity/oidc/token/{username}",
    headers={"Authorization": f"Bearer {vault_token}"}
  )
  return jsonify({"jwt": resp.json()["data"]["token"], "ttl": resp.json()["data"]["ttl"]})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
