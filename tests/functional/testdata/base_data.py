import uuid

id_super = "509a9e82-548e-466a-bda5-30dde928df87"
id_good_1 = str(uuid.uuid4())
id_good_2 = str(uuid.uuid4())
id_bad = str(uuid.uuid4())
id_role_without_role = "b0d1d6be-aa14-41fc-8b2f-4124f3b22ac3"
id_role_premium = "099761fa-7e65-4d75-aeaf-d1156a83dedd"
id_invalid = "definitely not ID"
id_invalid_blank = ""
invalid_secret_key = "fdsagasfhgsdfgasdfsa"
ids = [str(uuid.uuid4()) for _ in range(10)]
