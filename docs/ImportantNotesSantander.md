## Sobre el additionalUniversityUserData:

Para esta parte son dos casos por el valueType :
1. Cuando el type es text, en la app aparece el value, por eso en tu ejemplo solo ves el "A". En este caso deberías de poner en el value lo que quieras que se vea en la app
2. Cuando el type es link o image, el value funciona diferente ya que es el valor de la url y la imagen y en estos casos sale en la app el label, en el caso de los links y la imagen de la url con el label arriba en el caso de imagen

## "userUniversities[0].courses[0].type" is required
Debe de venir como este ejemplo, los datos aceptados en el type son [degree, master, doctorate, fp, subject, other, high school]

```json
    {
    "person": {
        "personName": {
            "givenName": "PARIS JORGE",
            "lastName": "SALMERON",
            "secondLastName": "AYALA"
        },
        "contactPoint": {
            "telephone": "(444) 444 4444",
            "emailAddress": "mail@uvaq.edu.mx"
        },
        "document": {
            "documentNumber": "CURP",
            "issuerEntityCountry": "MX"
        },
        "nationality": {
            "countryCode": "MX"
        },
        "birthDate": "YYYY-MM-DD"
    },
    "userUniversities": [
        {
            "userId": "user_id",
            "creationDate": "YYYY-MM-DD",
            "userImage": {
                "url": "https://siiu2015.uvaq.edu.mx:8444/siiuvaq/foto/administrativo/3973-44007-SAAP770628HMCLYR00.jpg"
            },
            "university": {
                "universityId": "2b0020f3-9d2f-4a14-b5b2-dcbad34754b5"
            },
            "role": {
                "name": "services"
            },
            "courses": [
                {
                    "name": ["Dept", "course_name"],
                    "type": "other"
                }
            ],
            "additionalUniversityUserData": [
                {
                    "label": "Face",
                    "value": "https://www.facebook.com/uvaqoficial",
                    "valueType": "link"
                },
                {
                    "label": "Grupo",
                    "value": "A",
                    "valueType": "text"
                },
                {
                    "label": "Image",
                    "value": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwJksRWkLgybSxiHatpg3FtU5xEgJhg4ZglQ&s",
                    "valueType": "image"
                }
            ]
        }
    ],
    "userNotificationsGroups": {
        "mandatory": [
            "rol [student, services, professor, tester]"
        ],
        "optional": [
            "TRES MARÍAS"
        ]
    }
}
```