
# Nimbus Frontend

A modern React (Vite + TypeScript) frontend for the Nimbus API.

## Features
- Secure login page (JWT auth)
- Event listing page (fetches from backend)
- API integration via environment variable
- TypeScript, React 18, Vite

## Getting Started

1. Install dependencies:
   ```sh
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```
3. The app runs at [http://localhost:5173](http://localhost:5173) and proxies API requests to [http://localhost:8000].

## Connecting to Backend
- The frontend expects the Nimbus API to be running locally at `http://localhost:8000`.
- Update `vite.config.ts` if your API runs elsewhere.

## Usage
- Login with your API credentials.
- View events after successful login.

## Customization
- Edit `src/LoginPage.tsx` and `src/EventsPage.tsx` for more features.

## Troubleshooting

- **Favicon 404**: If you see 404 errors for favicon, ensure `public/favicon.ico` and `public/favicon.svg` exist and are copied to the build output. The Dockerfile is patched to copy these files for production.
- **JWT Issues**: If event APIs return 401 Unauthorized, make sure you are logged in and using a fresh JWT token. If the token is expired, login again.
- **Event API 401**: The backend `/v1/events` POST endpoint expects HMAC authentication, not JWT. The frontend currently uses JWT for event listing and login. For event ingestion, use the backend's HMAC API or update the frontend to support HMAC headers.
- **Registration 409**: If you get a 409 Conflict on registration, the email is already registered. Use a new email.
- **Backend Migration Errors**: See the backend README for manual migration and index creation steps.

## Getting Started

1. Install dependencies:
   ```sh
   npm install
   ```
2. Set API URL in `.env`:
   ```sh
   VITE_API_URL=http://localhost:8000
   ```
3. Run development server:
   ```sh
   npm run dev
   ```

## Build for Production

```sh
npm run build
```

## Lint & Format

Add ESLint/Prettier for code quality:
```sh
npm install --save-dev eslint prettier eslint-plugin-react @typescript-eslint/eslint-plugin @typescript-eslint/parser
```

## Folder Structure
- `src/` - Main source code
- `LoginPage.tsx` - Login UI
- `EventsPage.tsx` - Event list UI
- `App.tsx` - Main app logic

## API Integration
- Set `VITE_API_URL` to your backend endpoint
- Uses JWT for authentication

## Security & Best Practices
- Never commit secrets
- Use HTTPS in production
- Validate API responses
- Use strong passwords

## Deployment
- Use Vite preview or serve with Nginx/Netlify/Vercel

---
For backend setup, see `../api/README.md`.
