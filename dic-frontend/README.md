# DIC Analyzer Frontend

A beautiful and modern Vue.js frontend for the DIC (Digital Image Correlation) analysis API.

## Features

- 🎨 Modern and responsive UI built with Vuetify
- 📊 Interactive dashboard with statistics and analytics
- 📁 File upload with drag-and-drop support and image preview
- 📋 Comprehensive analysis management with filtering and search
- 🖼️ Image visualization and comparison tools
- 📈 Real-time status updates and progress tracking
- 📥 Results download in ZIP format
- 🔄 Bulk operations for analysis management

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Vuetify** - Material Design component library
- **Pinia** - State management
- **Vue Router** - Official routing library
- **Axios** - HTTP client for API communication

## Project Structure

```
src/
├── assets/          # Static assets
├── components/      # Reusable Vue components
│   ├── AppNavigation.vue
│   └── AppFooter.vue
├── views/          # Page components
│   ├── DashboardView.vue
│   ├── AnalysisListView.vue
│   ├── AnalysisCreateView.vue
│   └── AnalysisDetailView.vue
├── router/         # Vue Router configuration
├── stores/         # Pinia stores
│   └── analysis.ts
├── services/       # API service layer
│   └── api.ts
├── types/          # TypeScript type definitions
│   └── api.ts
└── main.ts         # Application entry point
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Running DIC API backend (Django)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## API Integration

The frontend communicates with the DIC API backend. Make sure the backend is running on `http://localhost:8000`.

### Key API Endpoints Used

- `GET /api/analyses/` - List analyses with filtering
- `POST /api/analyses/` - Create new analysis
- `GET /api/analyses/{id}/` - Get analysis details
- `GET /api/analyses/stats/` - Get statistics
- `POST /api/analyses/{id}/cancel/` - Cancel analysis
- `GET /api/analyses/{id}/download/` - Download results

## Features Overview

### Dashboard
- Overview statistics and KPIs
- Recent analyses list
- Activity timeline
- Processing statistics

### Analysis Management
- Create new analyses with file upload
- List analyses with advanced filtering
- View detailed analysis results
- Cancel running analyses
- Download results as ZIP files

### Image Handling
- Drag-and-drop file upload
- Image preview before submission
- Side-by-side image comparison
- Displacement map visualization

### Responsive Design
- Mobile-first approach
- Adaptive layouts for all screen sizes
- Touch-friendly interactions

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

### Code Style

This project uses:
- ESLint for code linting
- Prettier for code formatting
- TypeScript for type safety

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
