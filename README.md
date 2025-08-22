# ML Model Deployment to AWS ECS (Fargate) with CI/CD (GitHub Actions)

This template shows how to deploy a **FastAPI** ML inference service packaged in **Docker** to **AWS ECS (Fargate)** with a full **CI/CD** pipeline using **GitHub Actions**.

---

## What you get

- **FastAPI app** that loads a scikit-learn model and exposes `POST /predict`.
- **Training script** that creates a tiny dummy regression model and saves it to `model.joblib`.
- **Dockerfile** to containerize the service.
- **ECS Task Definition** stub and **GitHub Actions workflow** to build & push to **Amazon ECR** and deploy to **ECS Fargate**.
- **Smoke tests** example.
- Production-minded structure with env vars, health endpoint, and graceful startup.

---

## Quick Start (Local)

1. Create and activate a virtual env (optional).
2. Install deps:
   ```bash
   pip install -r app/requirements.txt
   ```
3. Train a dummy model (creates `app/model.joblib`):
   ```bash
   python app/train.py
   ```
4. Run the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```
5. Try a request:
   ```bash
   curl -X POST http://localhost:8080/predict -H "Content-Type: application/json"      -d '{"feature1": 1.2, "feature2": 3.4}'
   ```

---

## Docker (Local)

```bash
# Build
docker build -t ml-fastapi:local .

# Run
docker run -p 8080:8080 ml-fastapi:local

# Test
curl -s http://localhost:8080/health
```

---

## AWS Prereqs (one-time)

1. **AWS Account & Region** (e.g., `ap-southeast-1` for Singapore).
2. **ECR Repository**: create `ml-fastapi` (or any name).
3. **ECS**:
   - Create **Cluster** (Fargate).
   - Create **Task Execution Role** (managed policy `AmazonECSTaskExecutionRolePolicy`).
   - (Optional) Create **Task Role** if your app needs AWS access (S3, Secrets Manager, etc.).
   - Create a **Service** (Fargate, 1+ tasks) using a public **Application Load Balancer**.
4. **VPC networking**:
   - Public subnets for ALB; private or public subnets for tasks.
   - **Security Groups** allowing ALB -> Task port (8080 by default).
5. **GitHub OIDC** (recommended) or long‑lived AWS keys:
   - Set up an **IAM Role for GitHub Actions** that allows: ECR (push), ECS (Describe/Update), IAM PassRole for the task exec role.
   - Trust policy for `token.actions.githubusercontent.com` (OIDC).

---

## CI/CD with GitHub Actions

- On each push to `main`:
  1. Build Docker image.
  2. Push image to **ECR**.
  3. Render ECS task definition with the new image tag.
  4. Update the ECS service (zero-downtime rolling deploy).
- Configure the following **GitHub Secrets** in your repo:
  - `AWS_ACCOUNT_ID`
  - `AWS_REGION` (e.g., `ap-southeast-1`)
  - `ECR_REPOSITORY` (e.g., `ml-fastapi`)
  - `ECS_CLUSTER` (e.g., `ml-cluster`)
  - `ECS_SERVICE` (e.g., `ml-service`)
  - `TASK_EXECUTION_ROLE_ARN` (your ECS task execution role ARN)
  - `AWS_ROLE_TO_ASSUME` (if using OIDC; Role ARN with ECR/ECS perms).

> If not using OIDC, provide `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` instead (less secure).

---

## ECS Concepts (Very Brief)

- **Image**: your packaged app.
- **ECR**: AWS Docker registry where your image is stored.
- **Task Definition**: JSON that declares **container(s)**, CPU/memory, ports, env vars.
- **Task**: a running instance of the task definition.
- **Service**: keeps the desired number of tasks running; handles rolling updates.
- **Cluster**: logical group of your services/tasks.
- **Fargate**: serverless compute for containers (no EC2 to manage).
- **ALB**: Load balancer that routes internet traffic to tasks.
- **CloudWatch**: Logs and metrics for monitoring/alerts.

---

## Deploy Manually Once (optional)

You can do a first deploy manually to create baselines:

```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t $ECR_REPOSITORY:manual .
docker tag $ECR_REPOSITORY:manual $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:manual
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:manual
```

Then create/update your ECS **Task Definition** with container image:
`$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:manual` and roll out the **Service**.

---

## Env Vars & Secrets

- Put non‑secret settings in the ECS Task Definition `environment` block.
- Put secrets in **AWS Secrets Manager** and mount via task definition or fetch at runtime.

---

## Health Checks & Autoscaling

- Health endpoint: `/health` returns 200 OK.
- Configure ALB health check path `/health` (HTTP 200).
- Enable **target tracking autoscaling** on the ECS service (CPU or request count).

---

## Rollbacks

- ECS keeps prior task definitions; if a deploy fails, revert to the previous revision.
- GitHub Actions step `amazon-ecs-deploy-task-definition` can wait for steady state and fail early.

---

## Files

- `app/main.py` – FastAPI app with `/predict` and `/health`.
- `app/train.py` – Dummy training script outputs `app/model.joblib`.
- `app/requirements.txt` – Python deps.
- `Dockerfile` – Container build.
- `infra/ecs-task-def.json` – Task Definition template.
- `.github/workflows/deploy.yml` – CI/CD pipeline.
- `tests/test_smoke.py` – simple test.

---

## License

Use freely for learning and projects. No warranty.
