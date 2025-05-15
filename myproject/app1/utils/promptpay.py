def generate_promptpay_payload(phone_number: str, amount: float) -> str:
    import crcmod

    def format_id(id_type, value):
        length = f"{len(value):02}"
        return f"{id_type}{length}{value}"

    def calculate_crc(payload):
        crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
        payload += '6304'
        crc = crc16(payload.encode('ascii'))
        return f"{crc:04X}"

    # แปลงเบอร์โทร
    if phone_number.startswith("0"):
        phone_number = "66" + phone_number[1:]
    elif not phone_number.startswith("66"):
        raise ValueError("หมายเลข PromptPay ต้องขึ้นต้นด้วย 0 หรือ 66")

    print(f"Converted phone number: {phone_number}")  # << ดูเบอร์หลังแปลง

    merchant_account = (
        format_id("00", "A000000677010111") +
        format_id("01", phone_number)
    )

    payload = ''
    payload += format_id("00", "01")
    payload += format_id("01", "11")
    payload += format_id("29", merchant_account)
    payload += format_id("52", "0000")
    payload += format_id("53", "764")
    payload += format_id("54", f"{amount:.2f}")
    payload += format_id("58", "TH")
    payload += format_id("59", "YourStore")
    payload += format_id("60", "Bangkok")
    payload += "6304"

    crc = calculate_crc(payload)
    full_payload = payload + crc

    print(f"Generated payload: {full_payload}")  # << ดู payload เต็ม

    return full_payload
