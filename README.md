# bravado_aioclient
Proof of concept for a asyncio based performant bravado HttpClient.

This is an absolute work in progress, and you should only try to use it to improve it!

## TODO

* use aiodns resolution
* write test suite, look at corner cases (files, forms ...)
* explore possible performance improvements with cython

## Does it work?

The get works! And exceptions are correctly raised

```
from bravado_aioclient import AIOClient
from bravado.client import SwaggerClient

client = SwaggerClient.from_url('http://petstore.swagger.io/v2/swagger.json', http_client=AIOClient())
no_pet_future = client.pet.getPetById(petId=-2)
pet_future = client.pet.getPetById(petId=42)

pet = pet_future.result()
no_pet = no_pet_future.result() # raises as expected
print(pet)
```
