import { Box, Button, Heading, Image, Spacer, Spinner, Text, useColorMode, useMediaQuery } from '@chakra-ui/react'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import colouredLogo from '/logo/svg/logo-color.svg';

function Home() {
    const [loading, setLoading] = useState(false);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const toggleLoading = () => {
        const newLoading = !loading;
        setLoading(newLoading);
        if (newLoading) {
            setTimeout(() => {
                setLoading(false);
            }, 3000);
        }
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px': '0px'}>
            <Box display={'flex'} flexDirection={limitedScreen ? 'column': 'row'} justifyContent={'space-between'} alignItems={'center'} mt={'20%'}>
                <Spacer />
                <Image src={colouredLogo} alt={'Logo'} maxH={{ base: '100px', md: '150px', lg: '200px' }} rounded={'xl'}/>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'left'} maxW={limitedScreen ? '70%': '50%'} p={!limitedScreen ? '10px': '0px'} mt={limitedScreen ? '20px': '0px'}>
                    <Heading as={'h1'} size={{ base: 'xl', md: '2xl'}}>Welcome to Access</Heading>
                    <Text mt={'10px'}>Access is a cloud storage service for all your quick, secure and efficient storage needs.</Text>
                    <br />
                    <Text>It's just two steps: Create an account and start uploading!</Text>
                    <br />
                    <Text>Access offers a variety of unique features like audit logs, share links and much more. What're you waiting for?</Text>
                    <br />
                    <Button variant={'Default'} size={'lg'} mt={'20px'} onClick={toggleLoading} isLoading={loading}>Get Started</Button>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default Home
