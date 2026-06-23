import os
import sys
import requests

PUBLIC_KEY = "public_Kk0Iqyw0BQmW0+Bq7C6CXnePPZ0="
URL_ENDPOINT = "https://ik.imagekit.io/fauziakhan10/"

print("=" * 60)
print("           AURA STORE - IMAGEKIT BATCH UPLOADER")
print("=" * 60)
print(f"URL Endpoint: {URL_ENDPOINT}")
print(f"Public Key:   {PUBLIC_KEY}\n")

# Use a standard input() so it can receive piped input safely in headless environments
private_key = input("Enter your ImageKit Private Key (starts with 'private_'): ").strip()
if not private_key.startswith("private_"):
    print("Error: The key must start with 'private_'. Please run the script again.")
    sys.exit(1)

# Folder path
media_products_dir = os.path.join(os.path.dirname(__file__), "media", "products")
if not os.path.exists(media_products_dir):
    print(f"Error: Directory {media_products_dir} not found. Are you running this in the project root?")
    sys.exit(1)

# Get all png files
files_to_upload = [f for f in os.listdir(media_products_dir) if f.endswith(".png")]
if not files_to_upload:
    print(f"No PNG files found in {media_products_dir}.")
    sys.exit(0)

print(f"\nFound {len(files_to_upload)} image(s) to upload in media/products/.\n")

session = requests.Session()
session.auth = (private_key, "")

success_count = 0
failed_files = []

for idx, filename in enumerate(files_to_upload, 1):
    file_path = os.path.join(media_products_dir, filename)
    print(f"[{idx}/{len(files_to_upload)}] Uploading {filename}...", end="", flush=True)
    
    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f, "image/png"),
            }
            data = {
                "fileName": filename,
                "folder": "media/products",
                "useUniqueFileName": "false",
            }
            
            response = session.post(
                "https://upload.imagekit.io/api/v1/files/upload",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                print(" [SUCCESS]")
                success_count += 1
            else:
                try:
                    err_msg = response.json().get("message", response.text)
                except Exception:
                    err_msg = response.text
                print(f" [FAILED] (Status {response.status_code}: {err_msg})")
                failed_files.append((filename, err_msg))
    except Exception as e:
        print(f" [ERROR] ({e})")
        failed_files.append((filename, str(e)))

print("\n" + "=" * 60)
print("                      UPLOAD SUMMARY")
print("=" * 60)
print(f"Successful uploads: {success_count}/{len(files_to_upload)}")
if failed_files:
    print("\nFailed files:")
    for fn, err in failed_files:
        print(f"  - {fn}: {err}")
else:
    print("\nAll files uploaded successfully! You are ready for production.")
print("=" * 60)
