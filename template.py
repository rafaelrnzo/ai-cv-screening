import os

# Define folder structure for AI microservice
structure = {
    "cmd": ["server.py"],
    "api/handlers": ["inference.py"],
    "api/routers": ["router.py"],
    "api/schemas": ["input.py", "output.py"],
    "ai_logic": ["preprocess.py", "model_inference.py", "postprocess.py"],
    "domain": ["entities.py", "exceptions.py", "services.py"],
    "repository": ["storage.py"],
    "external": ["api_client.py", "messaging.py"],
    "config": ["settings.py", "logging_config.py"],
    "infra/docker": ["Dockerfile"],
    "infra/kubernetes": [],
    "infra/scripts": ["deploy.sh"],
    "infra/ci_cd": [],
    "utils": ["logger.py", "helpers.py"],
    "tests/api": ["test_inference.py"],
    "tests/ai_logic": ["test_preprocess.py", "test_model_inference.py"],
    "tests/domain": ["test_services.py"],
    "model/v1": ["model_placeholder.txt", "metadata.json"],
    "model/v2": [],
}

# Create folders and files
base_path = "my_ai_service"
os.makedirs(base_path, exist_ok=True)

for folder, files in structure.items():
    path = os.path.join(base_path, folder)
    os.makedirs(path, exist_ok=True)
    for file in files:
        open(os.path.join(path, file), "w").close()

# Create top-level files
top_files = ["README.md", "requirements.txt", ".gitignore", ".env.sample"]
for f in top_files:
    open(os.path.join(base_path, f), "w").close()

print(f"✅ Struktur folder AI microservice berhasil dibuat di: {os.path.abspath(base_path)}")
