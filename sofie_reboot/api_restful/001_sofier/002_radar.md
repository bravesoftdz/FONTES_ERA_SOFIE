[TOC]

# Radar de Micro Tarefas



## API

**Request:**

`GET /micro_task/radar/`

- `lat`: Latitude do *sofier*
- `lng`: Longitude do *sofier*
- `radius`: Raio de abrangência

**Response:**

`200- OK`  

```json
{
    "data": [
         {
            "lat": -23.515108802616417,
            "lng": -46.80367559194565
        },
        {
            "lat": -23.515777969002485,
            "lng": -46.8003711104393
        },
        {
            "lat": -23.515805850935237,
            "lng": -46.800247728824615
        }
    ]
}
```


