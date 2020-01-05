# Fluxo de Venda

Para a execução de uma venda





```json
{
    "product_id": "0000-0000-0000-0000",
    "sofier": "sofier@gmail.com",
    "consumer": {
		"document": "99999999932",
        "name": "Cicrano de Tal",
        "email": "consumer@gmail.com",
        "birthdate": "1977-09-08",
        "telephony": "11988885555",
        "address": {
     		"city": "Osasco",
            "complement": "",
            "country": "Brasil",
            "district": "KM 18",
            "full_name": "Hildebrando de Lima",
            "number": "398",
            "postal_code": "06190160",
            "reference": "",
            "state": "SP",
            "type": "Avenida"
        }
    },
    "delivery_address": {
        "city": "Osasco",
        "complement": "",
        "country": "Brasil",
        "district": "KM 18",
        "full_name": "Hildebrando de Lima",
        "number": "398",
        "postal_code": "06190160",
        "reference": "",
        "state": "SP",
        "type": "Avenida"
    },
    "payment": {
        "modality": "CREDIT_CARD",
        "params": {
            "installments": 3,
            "credit_card": {
                "pin": "9999888877776666",
                "holder": "Fulano de Tal",
                "expiration": "06/27",
                "cvv": "999",
                "brand": "MASTERCARD"
            },
        }
    },
    "execution_flow": [        {
       "question": "Qual é a sua idade?",
        "response": 21,
        "input_style": "input_number", // number, string, radio, checkbox, memo, date, time, picture
        "type_response": "string", // string, number, list, url
    }]
}
```

