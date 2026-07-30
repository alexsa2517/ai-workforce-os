# Frontend

AI Workforce OS Frontend Application — a modern React + TypeScript SPA for managing AI employees, chatting with AI agents, and monitoring tasks.

## Tech Stack

| Layer       | Technology                   |
|-------------|------------------------------|
| Framework   | React 18 + TypeScript        |
| Build Tool  | Vite 5                       |
| Styling     | Inline CSS (dark theme)      |
| HTTP Client | Fetch API                    |

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

The development server starts on `http://localhost:3000` and proxies API requests to `http://localhost:8000`.

## Available Scripts

| Command         | Description                          |
|-----------------|--------------------------------------|
| `npm run dev`   | Start development server (HMR)       |
| `npm run build` | Production build (TypeScript check)  |
| `npm run preview`| Preview production build             |
| `npm run lint`  | Run ESLint with auto-fix             |
| `npm run typecheck` | TypeScript type checking only    |

## Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── services/       # API service layer
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript type definitions
│   ├── App.tsx         # Root component with routing
│   └── main.tsx        # Entry point
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Pages

**Dashboard** — System overview with key metrics, agent status, and recent activity.

**Chat Interface** — Real-time chat with AI agents. Supports provider switching (OpenAI, Gemini, DeepSeek).

**Agents View** — List and manage AI agents, view capabilities and status.

## Building for Production

```bash
npm run build
```

Output will be in `frontend/dist/`. Deploy this folder to any static hosting service.
