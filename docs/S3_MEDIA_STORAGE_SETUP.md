# S3 Media Storage Setup

This project uses private S3 storage for profile photos and intro videos.

Upload flow:

1. The frontend asks the FastAPI backend for an upload intent.
2. The backend returns a short-lived S3 presigned `PUT` URL.
3. The browser uploads the file directly to S3.
4. The frontend confirms the upload with the backend.
5. The backend checks the S3 object, stores `s3://bucket/key` in Postgres, and returns short-lived signed view URLs when media is loaded.

Keep the S3 bucket private. Do not create a public bucket policy for this app.

## Values Used By This Project

Local/dev bucket example:

```text
gaateh-dev-media-your-unique-suffix
```

Production bucket example:

```text
gaateh-prod-media-your-unique-suffix
```

Bucket names must be globally unique across S3, so replace `your-unique-suffix`
with something account-specific.

AWS region:

```text
ap-south-1
```

Region name in AWS console:

```text
Asia Pacific (Mumbai)
```

Frontend origins:

```text
http://localhost:3000
http://127.0.0.1:3000
https://gaateh.com
https://www.gaateh.com
```

## 1. Create The S3 Bucket

Open AWS Console:

```text
AWS Console > S3 > Create bucket
```

Use these settings:

```text
Bucket name: gaateh-dev-media-your-unique-suffix
AWS Region: Asia Pacific (Mumbai) ap-south-1
Object Ownership: ACLs disabled / Bucket owner enforced
Block Public Access: Block all public access ON
Bucket Versioning: optional, recommended for production
Default encryption: SSE-S3 is fine
```

For production, create a separate bucket:

```text
gaateh-prod-media-your-unique-suffix
```

Use the same region:

```text
ap-south-1
```

## 2. Add S3 CORS

Open:

```text
S3 > your bucket > Permissions > Cross-origin resource sharing (CORS) > Edit
```

Paste this:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": [
      "https://gaateh.com",
      "https://www.gaateh.com",
      "http://localhost:3000",
      "http://127.0.0.1:3000"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

If Next.js runs on another local port, add that exact origin too, for example:

```text
http://localhost:3001
```

Origins must match exactly: protocol, host, and port.

## 3. Create IAM Policy

Open:

```text
AWS Console > IAM > Policies > Create policy > JSON
```

For the local/dev bucket, paste this policy after replacing the bucket name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GaatehDevMediaObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::gaateh-dev-media-your-unique-suffix/photos/*",
        "arn:aws:s3:::gaateh-dev-media-your-unique-suffix/videos/*"
      ]
    }
  ]
}
```

Name it:

```text
GaatehDevMediaS3Policy
```

For production, create a separate policy and replace the bucket name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GaatehProdMediaObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::gaateh-prod-media-your-unique-suffix/photos/*",
        "arn:aws:s3:::gaateh-prod-media-your-unique-suffix/videos/*"
      ]
    }
  ]
}
```

Name it:

```text
GaatehProdMediaS3Policy
```

## 4. Create IAM User And Access Key

For local/dev or for a backend running outside AWS:

```text
AWS Console > IAM > Users > Create user
```

Use:

```text
User name: gaateh-dev-api-s3
Console access: no
Permissions: Attach policies directly
Policy: GaatehDevMediaS3Policy
```

Then create the access key:

```text
IAM > Users > gaateh-dev-api-s3 > Security credentials > Create access key
```

Choose:

```text
Application running outside AWS
```

Copy these values immediately:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

Do not put AWS keys in the frontend. Do not use `NEXT_PUBLIC_` for AWS secrets.

For production, create a separate user:

```text
gaateh-prod-api-s3
```

Attach:

```text
GaatehProdMediaS3Policy
```

## 5. Configure Backend Env

Local backend file:

```text
backend/.env
```

The FastAPI app reads `backend/.env`. The repo-root `.env.example` is only a
combined reference file.

Use this for local/dev:

```env
APP_ENV=development
APP_DEBUG=true

BACKEND_CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_ALLOWED_ORIGINS=http://localhost:3000

AWS_REGION=ap-south-1
AWS_S3_BUCKET=gaateh-dev-media-your-unique-suffix
AWS_ACCESS_KEY_ID=PASTE_YOUR_DEV_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=PASTE_YOUR_DEV_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=
AWS_S3_PHOTOS_PREFIX=photos
AWS_S3_VIDEOS_PREFIX=videos
AWS_S3_UPLOAD_URL_EXPIRES_SECONDS=900
AWS_S3_VIEW_URL_EXPIRES_SECONDS=900
```

Use this for production:

```env
APP_ENV=production
APP_DEBUG=false

BACKEND_CORS_ORIGINS=https://gaateh.com,https://www.gaateh.com
FRONTEND_ALLOWED_ORIGINS=https://gaateh.com,https://www.gaateh.com

AWS_REGION=ap-south-1
AWS_S3_BUCKET=gaateh-prod-media-your-unique-suffix
AWS_ACCESS_KEY_ID=PASTE_YOUR_PROD_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=PASTE_YOUR_PROD_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=
AWS_S3_PHOTOS_PREFIX=photos
AWS_S3_VIDEOS_PREFIX=videos
AWS_S3_UPLOAD_URL_EXPIRES_SECONDS=900
AWS_S3_VIEW_URL_EXPIRES_SECONDS=900
```

Restart the backend after changing `.env`.

If the backend runs on AWS, prefer an IAM role attached to the runtime. In that
case, keep the AWS access key fields empty and set only `AWS_REGION`,
`AWS_S3_BUCKET`, and the prefixes.

## 6. Configure Frontend Env

Local file:

```text
frontend/.env.local
```

Local:

```env
NEXT_PUBLIC_APP_NAME=Gaateh
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=PASTE_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=PASTE_SUPABASE_ANON_KEY
```

Production:

```env
NEXT_PUBLIC_APP_NAME=Gaateh
NEXT_PUBLIC_API_BASE_URL=https://api.gaateh.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=PASTE_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=PASTE_SUPABASE_ANON_KEY
```

## 7. Run Database Migrations

Local development usually runs migrations on startup.

For production, run:

```bash
cd backend
alembic upgrade head
```

The S3 metadata columns are added by:

```text
backend/app/db/migrations/versions/0005_add_media_storage_metadata.py
```

## 8. Start Locally

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

## 9. Verify Uploads

Upload a profile photo from the app.

Backend logs should show:

```text
OPTIONS /api/v1/media/photos/upload-intent 200 OK
POST /api/v1/media/photos/upload-intent 200 OK
POST /api/v1/media/photos/confirm 201 Created
```

In Chrome DevTools > Network, the direct S3 upload should be:

```text
PUT https://gaateh-dev-media-your-unique-suffix.s3.ap-south-1.amazonaws.com/photos/...
```

Expected result:

```text
Status: 200
```

Then check S3:

```text
S3 > gaateh-dev-media-your-unique-suffix > photos/<user-id>/
```

You should see the uploaded image.

The database should store:

```text
provider = s3
bucket = gaateh-dev-media-your-unique-suffix
object_key = photos/<user-id>/<file-id>.jpg
photo_url = s3://gaateh-dev-media-your-unique-suffix/photos/<user-id>/<file-id>.jpg
```

The API response from:

```text
GET /api/v1/media/photos/me
```

should return a temporary signed `photo_url`.

## Troubleshooting

### Backend upload-intent is not called

Check frontend env:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Restart the frontend after changing `frontend/.env.local`.

### Backend upload-intent returns 503

Check backend env:

```env
AWS_REGION=ap-south-1
AWS_S3_BUCKET=gaateh-dev-media-your-unique-suffix
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

For an AWS-hosted backend, make sure the attached IAM role has the same S3
permissions. Restart the backend after changing `backend/.env`.

### Browser says Failed to fetch after upload-intent succeeds

This usually means the direct S3 `PUT` failed.

Check Chrome DevTools > Network:

```text
OPTIONS https://gaateh-dev-media-your-unique-suffix.s3.ap-south-1.amazonaws.com/...
PUT https://gaateh-dev-media-your-unique-suffix.s3.ap-south-1.amazonaws.com/...
```

If `OPTIONS` fails, fix S3 CORS.

If `PUT` returns `403`, check:

```text
AWS_REGION matches the bucket region
AWS_S3_BUCKET is the correct bucket
IAM policy allows s3:PutObject on photos/* and videos/*
Backend was restarted after env changes
```

### Wrong S3 region in request URL

The URL must include:

```text
s3.ap-south-1.amazonaws.com
```

If it does not, check:

```env
AWS_REGION=ap-south-1
```

Then restart the backend.

### Confirm endpoint says object not found

The browser upload did not actually finish before confirm, or it uploaded to a different key.

Check the failed S3 request in DevTools and make sure the `PUT` status is `200`.

## Security Notes

- Keep the bucket private.
- Keep Block Public Access enabled.
- Do not add a public bucket policy.
- Do not put AWS keys in frontend env files.
- Use separate dev and production buckets.
- Use separate dev and production IAM users or roles.
- Rotate AWS access keys if they are exposed.
- Prefer an IAM role instead of long-lived access keys if the backend is deployed on AWS.
