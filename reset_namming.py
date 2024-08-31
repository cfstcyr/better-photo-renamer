import os
import uuid


PATH = "/Users/charles-francoisst-cyr/Library/CloudStorage/ProtonDrive-cfstcyr@pm.me-folder/Photos/2024/08 Août - Rome"

for filename in os.listdir(PATH):
    if filename == ".DS_Store":
        continue

    path = os.path.join(PATH, filename)
    os.rename(
        os.path.join(PATH, filename),
        os.path.join(PATH, uuid.uuid4().hex + os.path.splitext(filename)[1]),
    )
