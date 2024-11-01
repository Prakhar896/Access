import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from './components/ui/provider.jsx'
import { defaultSystem } from "@chakra-ui/react"
import { configureStore } from '@reduxjs/toolkit'
import AccessTheme from './themes/AccessTheme.js'
import universalReducer from './slices/UniversalState.js'
import './index.css'
import App from './App.jsx'

const store = configureStore({
    reducer: {
        universal: universalReducer
    }
})

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <Provider value={AccessTheme}>
            <App />
        </Provider>
    </StrictMode>,
)
