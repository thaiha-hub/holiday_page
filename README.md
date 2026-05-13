# Holiday Page

A serverless web application that shows today's date and whether it is a Swedish public holiday, half-day, or bridge day. Data is fetched from the [Dagsmart API](https://dagsmart.se/api/).

## Architecture

```
User → CloudFront → S3 (frontend)
                       ↓ (app.js)
             API Gateway → Lambda → Dagsmart API
```

| Layer | Service |
|---|---|
| Frontend hosting | Amazon S3 (static website) |
| CDN / HTTPS | Amazon CloudFront |
| API | Amazon API Gateway (HTTP API) |
| Backend | AWS Lambda (Python) |
| External data | Dagsmart API |

## Project structure

```
holiday_page/
├── frontend/
│   ├── index.html      # UI
│   └── app.js          # Fetches data from API Gateway
└── lambda/
    └── handler.py      # Lambda function
```

## How it works

1. The user opens the CloudFront URL.
2. CloudFront serves `index.html` and `app.js` from S3.
3. `app.js` calls `GET /today` on API Gateway.
4. API Gateway triggers the Lambda function.
5. Lambda fetches data from Dagsmart API (`/holidays`, `/half-days`, `/bridge-days`), filters for today's date, and returns a JSON response.
6. The page displays the date and any matching holidays, half-days, or bridge days.

## Deployment

Deployment is automated with GitHub Actions. On every push to `main`, the workflow:

1. Packages `handler.py` into `function.zip`
2. Updates the Lambda function code
3. Waits for the Lambda update to complete
4. Syncs frontend files to S3
5. Creates a CloudFront invalidation (`/*`)

### Required GitHub secrets / variables

| Name | Type | Description |
|---|---|---|
| `AWS_ROLE_ARN` | Secret | ARN of the IAM role to assume via OIDC |
| `LAMBDA_FUNCTION_NAME` | Secret | Name of the Lambda function |
| `S3_BUCKET` | Secret | S3 bucket name |
| `CLOUDFRONT_DISTRIBUTION_ID` | Secret | CloudFront distribution ID |
| `AWS_REGION` | Variable | AWS region (e.g. `eu-north-1`) |

The workflow uses GitHub OIDC to authenticate with AWS. The IAM role must trust the GitHub OIDC provider (`token.actions.githubusercontent.com`) and include a condition scoped to this repository.

## Lambda API response

`GET /today` returns:

```json
{
  "date": "2026-05-09",
  "holidays": [],
  "halfDays": [],
  "bridgeDays": []
}
```

## Known limitations

- S3 bucket requires public read access (S3 static website hosting).
- CORS is restricted to the CloudFront domain.
- Lambda calls Dagsmart API on every request with no caching.

## Possible improvements

- CloudFront Origin Access Control (OAC) with a private S3 bucket
- Infrastructure as code with OpenTofu
- CloudWatch Alarms for Lambda errors and API Gateway 5xx responses
- Cache Dagsmart API responses in S3 or DynamoDB
- Add AWS WAF in front of CloudFront
