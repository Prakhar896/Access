import { Box, Button, Heading, Text } from '@chakra-ui/react'
import { useState } from 'react'
import { useSelector } from 'react-redux'

function Home() {
    const [count, setCount] = useState(0)
    const { username, error } = useSelector(state => state.auth)
    
    const increment = () => { setCount(count + 1) }

    return (
        <Box p={20}>
            <Heading as={"h1"}>{!username ? "Hello!": "Hi " + username + "!"}</Heading>
            <Text>Welcome back!</Text>
            {error && <Text color={'red'}>{error}</Text>}
            <Text>{count}</Text>
            <Button onClick={increment} variant={'Default'}>Increment</Button>
        </Box>
    )
}

export default Home
