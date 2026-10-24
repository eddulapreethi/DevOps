# Recipe Organizer

A Flask recipe organizer with a home page, searchable recipe collection, recipe
details, and a form for adding recipes. The initial collection contains three
sample recipes. Recipes are stored in SQLite.

## Run locally

From this folder:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. Run the tests with:

```powershell
python -m pip install pytest
python -m pytest -v tests
```

Build and run the container:

```powershell
docker build -t recipe-organizer .
docker run --rm -p 5000:5000 recipe-organizer
```

## Jenkins and Kubernetes

Configure Jenkins to check out the repository root and set the pipeline script
path to `CaseStudy/Jenkinsfile`. The Jenkins agent needs Python, Docker, and
`kubectl`, plus access to the target Kubernetes cluster. Add a Jenkins
username/password credential with ID `dockerhub-credentials`; use a Docker Hub
access token as its password (the username should be `eddulapreethi`). The
pipeline tests the app, builds and pushes versioned and `latest` images to
`eddulapreethi/simple_demo`, then applies the Kubernetes manifests and waits for
the deployment rollout.

The Kubernetes Service is a NodePort on `30080`. After deployment, access
`http://<node-address>:30080`; the app health endpoint is `/healthz`.

The demo uses a single pod because each pod stores its SQLite database locally.
The database is not backed by a persistent volume, so recipes added at runtime
are not preserved when the pod is replaced.
