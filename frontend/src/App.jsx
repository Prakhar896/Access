import { Box, Button, Heading, Text } from '@chakra-ui/react'
import { useState } from 'react'

function App() {
    const [count, setCount] = useState(0)
    
    const increment = () => { setCount(count + 1) }

    return (
        <Box>
            <Heading as={"h1"}>Hello, World!</Heading>
            <Text>Welcome back!</Text>
            <Text>{count}</Text>
            <Button onClick={increment} variant={'Default'}>Increment</Button>
        </Box>
    )
}

export default App
