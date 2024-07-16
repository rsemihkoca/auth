



@app.get("/client/{mac_address}", response_model=BrokerAuthenticationResponse)
def get_client_status(mac_address: str, request: BrokerAuthenticationRequest, db: Session = Depends(get_db)):

    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        app.logger.info(f"Client not found: {mac_address}")
        return BrokerAuthenticationResponse(result="deny")

    if client.is_disabled:
        app.logger.info(f"Client is disabled: {mac_address}")
        return BrokerAuthenticationResponse(result="deny")

    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()

    if hashed_password != client.password:
        app.logger.info(f"Invalid password: {mac_address}")
        return BrokerAuthenticationResponse(result="deny")

    return BrokerAuthenticationResponse(result="allow", is_superuser=client.is_superuser)
