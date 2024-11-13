import { Box, Button, Heading, Image, Text, useColorMode } from '@chakra-ui/react'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import colouredLogo from '/logo/svg/logo-color.svg';

function Home() {
    const { colorMode, toggleColorMode } = useColorMode();

    return (
        <Box mt={{ base: '20px', lg: '30px' }} display={'flex'} flexDirection={'row'} maxW={'100%'} p={'10px'}>
            <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
            <Button onClick={toggleColorMode} variant={'Default'}>
                Toggle {colorMode === 'light' ? 'Dark' : 'Light'}
            </Button>
        </Box>
    )
}

export default Home
