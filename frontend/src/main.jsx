import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ChakraProvider } from '@chakra-ui/react'
import './index.css'

import App from './App.jsx'

const store = configureStore({
    reducer: {
        universal: universalReducer,
        auth: authReducer
    }
})

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <ChakraProvider>
            <App />
        </ChakraProvider>
    </StrictMode>,
)
