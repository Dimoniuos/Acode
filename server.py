from py3xui import Api, Client, Inbound, AsyncApi

import time

def get_connection_string(inbound: Inbound, user_email: int|str) -> str:
    public_key = inbound.stream_settings.reality_settings.get("settings").get("publicKey")
    short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]
    connection_string = (
        f"vless://{user_email}@79.137.203.114:8443/"
        f"?type=tcp&security=reality&pbk={public_key}&fp=randomized&sni=yahoo.com"
        f"&sid={short_id}&spx=%2F#{user_email}"
    )
    #connection_string = "test_connection_string"
    return connection_string

async def new_user(id, days, inbound, api):
    await api.client.add(1, [Client(id=str(id), tg_id=str(id), enable=True, expiry_time=int(time.time()) * 1000 + days * 24 * 3600 * 1000, email=str(id))])

def list_active_users(inbound):
    clients = inbound.settings.clients
    answer = []
    for client in clients:
        if client.enable:
            answer.append(client.id)
    return answer

def get_expiration_dates(inbound):
    clients = inbound.settings.clients
    answer = []
    for client in clients:
        if client.enable:
            if client.expiry_time != 0:
                answer.append((int((client.expiry_time // 1000 - time.time()) // 3600 // 24), int((client.expiry_time // 1000 - time.time()) // 3600 % 24) ,int(client.email)))
    return answer
def get_expiration_dates_sl(inbound):
    clients = inbound.settings.clients
    answer = {}
    for client in clients:
        if client.enable:
            if client.expiry_time != 0:
                answer[client.id] = (int((client.expiry_time // 1000 - time.time()) // 3600 // 24), int((client.expiry_time // 1000 - time.time()) // 3600 % 24))
    return answer
async def prolong_subscriptions(id, api, days, inbound):
    client = None
    for c in inbound.settings.clients:
        if c.email == id:
            client = c
            break
    if client is None:
        await new_user(id, days, inbound, api)
        return
    cliend_uuid = client.id
    client_by_email = await api.client.get_by_email(id)
    client_by_email.expiry_time = int(max(client_by_email.expiry_time - time.time() * 1000, 0) + time.time() * 1000 + days * 24 * 3600 * 1000)
    client_by_email.id = cliend_uuid
    await api.client.update(client_by_email.id, client_by_email)