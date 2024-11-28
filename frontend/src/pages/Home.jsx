import { Box, Button, ButtonGroup, Heading, Image, Slide, Spacer, Spinner, Text, useColorMode, useMediaQuery } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import colouredLogo from '/logo/svg/logo-color.svg';
import { Link, useNavigate } from 'react-router-dom';
import CentredSpinner from '../components/CentredSpinner';
import { motion } from 'framer-motion';

function Home() {
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const navigate = useNavigate();
    const { username, loaded, error } = useSelector(state => state.auth);

    const toSignup = () => {
        navigate('/signup');
    }

    const toLogin = () => {
        navigate('/login');
    }

    useEffect(() => {
        if (username && loaded) {
            navigate('/portal/files');
        }
    }, [username, loaded]);

    if (!loaded) {
        return <CentredSpinner />
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, type: 'spring', stiffness: 100 }}
            >
                <Box display={'flex'} flexDirection={limitedScreen ? 'column' : 'row'} justifyContent={'space-between'} alignItems={'center'} mt={'20%'}>
                    <Spacer />
                    <Image src={colouredLogo} alt={'Logo'} maxH={{ base: '100px', md: '150px', lg: '200px' }} rounded={'xl'} />
                    <Spacer />
                    <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'flex-start'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                        <Heading as={'h1'} size={{ base: 'xl', md: '2xl' }}>Welcome to Access</Heading>
                        <Text mt={'10px'}>Access is a cloud storage service for all your quick, secure and efficient storage needs.</Text>
                        <br />
                        <Text>It's just two steps: Create an account and start uploading!</Text>
                        <br />
                        <Text>Access offers a variety of unique features like audit logs, share links and much more. What're you waiting for?</Text>
                        <br />
                        <ButtonGroup variant='Default' spacing='6'>
                            <Button onClick={toSignup} w={{ base: 'fit-content', lg: '120px' }}>Sign up</Button>
                            <Button onClick={toLogin} w={{ base: 'fit-content', lg: '120px' }}>Login</Button>
                        </ButtonGroup>
                        <Button variant={'link'} color={'black'} onClick={() => navigate('/forgotPassword')} mt={"20px"} fontSize={"sm"} >Forgot Password</Button>
                    </Box>
                    <Spacer />
                </Box>
            </motion.div>
        </Box>
    )
}

export default Home
