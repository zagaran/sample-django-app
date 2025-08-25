import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# Constants
DOTENV_PATH = os.path.join("config", ".env")
VECTOR_STORE_NAME = "sample-django-app"

INCLUDE_FILENAMES = {
    "Dockerfile",
}
INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".html",
    ".css",
    ".json",
    ".md",
}

# Load environment variables
load_dotenv(dotenv_path=DOTENV_PATH)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in config/.env")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Try to find existing vector store
existing_vector_stores = client.vector_stores.list().data
vector_store = next(
    (vs for vs in existing_vector_stores if vs.name == VECTOR_STORE_NAME),
    None
)

if vector_store:
    print(f"Found existing vector store: {vector_store.id}")
else:
    print(f"Creating new vector store: {VECTOR_STORE_NAME}")
    vector_store = client.vector_stores.create(name=VECTOR_STORE_NAME)

# Get set of files tracked by Git (respects .gitignore)
git_files = set()
try:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    git_files = set(output.strip().splitlines())
except subprocess.CalledProcessError:
    print("Warning: Not a Git repo or failed to get tracked files")

# Walk through repo and upload valid files
for root, _, files in os.walk("."):
    for fname in files:
        if fname == "__init__.py":
            continue

        fpath = os.path.join(root, fname)
        rel_fpath = os.path.relpath(fpath, start=".")  # Normalize path

        _, ext = os.path.splitext(fname)
        if (
            ext in INCLUDE_EXTENSIONS
            or fname in INCLUDE_FILENAMES
        ) and rel_fpath in git_files:

            try:
                print(f"Uploading {rel_fpath}...")
                with open(fpath, "rb") as f:
                    client.vector_stores.files.upload_and_poll(
                        vector_store_id=vector_store.id,
                        file=f
                    )
            except Exception as e:
                print(e)

