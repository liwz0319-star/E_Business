# Component Inventory

## UI Components (`/components`)

| Component | Type | Description |
|---|---|---|
| `App.tsx` | Layout/Logic | Root component, manages view state and API orchestration. |
| `Sidebar.tsx` | Navigation | Main app navigation menu. |
| `Header.tsx` | Layout | Top bar with theme toggle and notifications. |
| `Hero.tsx` | Display | Home screen hero section. |
| `GeminiResult.tsx` | Display | **Critical**. Displays AI output (text/img/video) and loading states. |
| `Editor.tsx` | Feature | Text/Content editor interface. |
| `Gallery.tsx` | Feature | Grid view of generated assets. |
| `AssetDetail.tsx` | Modal/Page | Detailed view of an asset. |
| `Login.tsx` | Auth | Mock login screen. |
| `PricingModal.tsx` | Modal | Subscription UI. |
| `Settings.tsx` | Feature | App configuration. |
| `Insights.tsx` | Feature | Data visualization (charts/stats). |
| `Projects.tsx` | Feature | Project management list. |
| `VideoDetail.tsx` | Feature | Specialized video player view. |
| `ImageEditor.tsx` | Feature | Canvas/Tool for editing images. |

## External Dependencies
- `react`: Core library
- `react-dom`: DOM binding
- `@google/genai`: AI SDK
